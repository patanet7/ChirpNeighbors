"""
LoRA Training Script for Bird Species Image Generation

Trains LoRA adapters on SDXL Turbo for specific bird families.
"""

import argparse
import logging
import os
from pathlib import Path
from typing import Optional

import torch
import wandb
import yaml
from accelerate import Accelerator
from accelerate.logging import get_logger
from accelerate.utils import ProjectConfiguration, set_seed
from diffusers import AutoencoderKL, DDPMScheduler, UNet2DConditionModel
from diffusers.optimization import get_scheduler
from diffusers.training_utils import EMAModel
from peft import LoraConfig, get_peft_model
from torch.utils.data import DataLoader
from tqdm.auto import tqdm
from transformers import CLIPTextModel, CLIPTokenizer

from data.bird_dataset import BirdDataset
from utils.metrics import calculate_clip_score, calculate_fid

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Train LoRA for bird image generation")
    parser.add_argument(
        "--config",
        type=str,
        default="../config/model_config.yaml",
        help="Path to config file",
    )
    parser.add_argument(
        "--bird_family",
        type=str,
        required=True,
        help="Bird family to train (e.g., passeriformes)",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="../models/lora",
        help="Output directory for trained LoRA",
    )
    parser.add_argument(
        "--resume_from_checkpoint",
        type=str,
        default=None,
        help="Path to checkpoint to resume from",
    )
    parser.add_argument(
        "--push_to_hub",
        action="store_true",
        help="Push model to Hugging Face Hub",
    )
    parser.add_argument(
        "--hub_model_id",
        type=str,
        default=None,
        help="Hugging Face Hub model ID",
    )
    return parser.parse_args()


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def setup_models(config: dict, accelerator: Accelerator) -> tuple:
    """
    Load and configure base models for training.

    Returns:
        Tuple of (tokenizer, text_encoder, vae, unet, noise_scheduler)
    """
    # Load tokenizer and text encoder
    tokenizer = CLIPTokenizer.from_pretrained(
        config["base_model"]["name"],
        subfolder="tokenizer",
        revision=config["base_model"]["revision"],
    )

    text_encoder = CLIPTextModel.from_pretrained(
        config["base_model"]["name"],
        subfolder="text_encoder",
        revision=config["base_model"]["revision"],
        variant=config["base_model"]["variant"],
    )

    # Load VAE
    vae = AutoencoderKL.from_pretrained(
        config["base_model"]["vae"]["name"],
        revision=config["base_model"]["revision"],
        variant=config["base_model"]["variant"],
    )

    # Load UNet
    unet = UNet2DConditionModel.from_pretrained(
        config["base_model"]["name"],
        subfolder="unet",
        revision=config["base_model"]["revision"],
        variant=config["base_model"]["variant"],
    )

    # Freeze base models
    vae.requires_grad_(False)
    text_encoder.requires_grad_(False)
    unet.requires_grad_(False)

    # Apply LoRA to UNet
    lora_config = LoraConfig(
        r=config["lora"]["rank"],
        lora_alpha=config["lora"]["alpha"],
        lora_dropout=config["lora"]["dropout"],
        target_modules=config["lora"]["target_modules"],
        init_lora_weights="gaussian",
    )

    unet = get_peft_model(unet, lora_config)
    unet.print_trainable_parameters()

    # Create noise scheduler
    noise_scheduler = DDPMScheduler.from_pretrained(
        config["base_model"]["name"],
        subfolder="scheduler",
    )

    # Move to device
    text_encoder.to(accelerator.device)
    vae.to(accelerator.device)

    return tokenizer, text_encoder, vae, unet, noise_scheduler


def create_dataloader(
    config: dict, bird_family: str, tokenizer: CLIPTokenizer, accelerator: Accelerator
) -> DataLoader:
    """Create training dataloader."""
    dataset = BirdDataset(
        data_dir=Path(config["dataset"]["local_path"]) / bird_family,
        tokenizer=tokenizer,
        resolution=config["generation"]["default_resolution"],
        augmentation_config=config["training"]["augmentation"],
    )

    dataloader = DataLoader(
        dataset,
        batch_size=config["training"]["train_batch_size"],
        shuffle=True,
        num_workers=4,
        pin_memory=True,
    )

    return dataloader


def train_epoch(
    epoch: int,
    unet: UNet2DConditionModel,
    vae: AutoencoderKL,
    text_encoder: CLIPTextModel,
    noise_scheduler: DDPMScheduler,
    dataloader: DataLoader,
    optimizer: torch.optim.Optimizer,
    lr_scheduler: torch.optim.lr_scheduler.LRScheduler,
    accelerator: Accelerator,
    config: dict,
) -> float:
    """
    Train for one epoch.

    Returns:
        Average loss for the epoch
    """
    unet.train()
    total_loss = 0.0

    progress_bar = tqdm(
        total=len(dataloader),
        desc=f"Epoch {epoch}",
        disable=not accelerator.is_local_main_process,
    )

    for step, batch in enumerate(dataloader):
        with accelerator.accumulate(unet):
            # Convert images to latent space
            latents = vae.encode(batch["images"].to(accelerator.device)).latent_dist.sample()
            latents = latents * vae.config.scaling_factor

            # Sample noise
            noise = torch.randn_like(latents)
            bsz = latents.shape[0]

            # Sample timesteps
            timesteps = torch.randint(
                0,
                noise_scheduler.config.num_train_timesteps,
                (bsz,),
                device=latents.device,
            )
            timesteps = timesteps.long()

            # Add noise to latents
            noisy_latents = noise_scheduler.add_noise(latents, noise, timesteps)

            # Get text embeddings
            encoder_hidden_states = text_encoder(batch["input_ids"].to(accelerator.device))[0]

            # Predict noise
            model_pred = unet(noisy_latents, timesteps, encoder_hidden_states).sample

            # Calculate loss
            loss = torch.nn.functional.mse_loss(model_pred.float(), noise.float(), reduction="mean")

            # Backprop
            accelerator.backward(loss)

            if accelerator.sync_gradients:
                accelerator.clip_grad_norm_(unet.parameters(), config["training"]["max_grad_norm"])

            optimizer.step()
            lr_scheduler.step()
            optimizer.zero_grad()

        # Logging
        if accelerator.sync_gradients:
            progress_bar.update(1)
            total_loss += loss.detach().item()

            if accelerator.is_main_process:
                # Log to wandb
                wandb.log(
                    {
                        "train_loss": loss.detach().item(),
                        "learning_rate": lr_scheduler.get_last_lr()[0],
                        "epoch": epoch,
                        "step": step,
                    }
                )

        # Save checkpoint
        if step > 0 and step % config["training"]["save_steps"] == 0:
            if accelerator.is_main_process:
                save_checkpoint(unet, optimizer, lr_scheduler, epoch, step, config)

    progress_bar.close()
    avg_loss = total_loss / len(dataloader)
    return avg_loss


def save_checkpoint(
    unet: UNet2DConditionModel,
    optimizer: torch.optim.Optimizer,
    lr_scheduler: torch.optim.lr_scheduler.LRScheduler,
    epoch: int,
    step: int,
    config: dict,
) -> None:
    """Save training checkpoint."""
    checkpoint_dir = Path(config["training"]["output_dir"]) / f"checkpoint-{epoch}-{step}"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # Save LoRA weights
    unet.save_pretrained(checkpoint_dir / "unet")

    # Save optimizer and scheduler
    torch.save(
        {
            "optimizer": optimizer.state_dict(),
            "lr_scheduler": lr_scheduler.state_dict(),
            "epoch": epoch,
            "step": step,
        },
        checkpoint_dir / "optimizer.pt",
    )

    logger.info(f"Saved checkpoint to {checkpoint_dir}")


def main() -> None:
    """Main training function."""
    args = parse_args()
    config = load_config(args.config)

    # Setup accelerator
    accelerator_project_config = ProjectConfiguration(
        project_dir=args.output_dir,
        logging_dir=Path(args.output_dir) / "logs",
    )

    accelerator = Accelerator(
        gradient_accumulation_steps=config["training"]["gradient_accumulation_steps"],
        mixed_precision=config["training"]["mixed_precision"],
        log_with="wandb" if config["monitoring"]["wandb"]["enabled"] else None,
        project_config=accelerator_project_config,
    )

    # Setup logging
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.INFO,
    )

    logger.info(accelerator.state, main_process_only=False)

    # Set seed
    set_seed(config["training"]["seed"])

    # Initialize wandb
    if accelerator.is_main_process and config["monitoring"]["wandb"]["enabled"]:
        wandb.init(
            project=config["monitoring"]["wandb"]["project"],
            entity=config["monitoring"]["wandb"]["entity"],
            name=f"lora-{args.bird_family}",
            config=config,
        )

    # Load models
    logger.info("Loading models...")
    tokenizer, text_encoder, vae, unet, noise_scheduler = setup_models(config, accelerator)

    # Create dataloader
    logger.info(f"Loading dataset for {args.bird_family}...")
    dataloader = create_dataloader(config, args.bird_family, tokenizer, accelerator)

    # Setup optimizer
    optimizer = torch.optim.AdamW(
        unet.parameters(),
        lr=config["training"]["learning_rate"],
        betas=(config["training"]["adam_beta1"], config["training"]["adam_beta2"]),
        weight_decay=config["training"]["weight_decay"],
        eps=config["training"]["adam_epsilon"],
    )

    # Setup learning rate scheduler
    lr_scheduler = get_scheduler(
        config["training"]["lr_scheduler"],
        optimizer=optimizer,
        num_warmup_steps=config["training"]["lr_warmup_steps"],
        num_training_steps=config["training"]["num_train_epochs"] * len(dataloader),
    )

    # Prepare for training
    unet, optimizer, dataloader, lr_scheduler = accelerator.prepare(
        unet, optimizer, dataloader, lr_scheduler
    )

    # Training loop
    logger.info("***** Running training *****")
    logger.info(f"  Num examples = {len(dataloader.dataset)}")
    logger.info(f"  Num epochs = {config['training']['num_train_epochs']}")
    logger.info(f"  Batch size = {config['training']['train_batch_size']}")
    logger.info(f"  Gradient accumulation steps = {config['training']['gradient_accumulation_steps']}")
    logger.info(f"  Total optimization steps = {config['training']['num_train_epochs'] * len(dataloader)}")

    for epoch in range(config["training"]["num_train_epochs"]):
        avg_loss = train_epoch(
            epoch,
            unet,
            vae,
            text_encoder,
            noise_scheduler,
            dataloader,
            optimizer,
            lr_scheduler,
            accelerator,
            config,
        )

        logger.info(f"Epoch {epoch} - Average loss: {avg_loss:.4f}")

        # Save final checkpoint
        if accelerator.is_main_process:
            save_checkpoint(unet, optimizer, lr_scheduler, epoch, len(dataloader), config)

    # Save final model
    if accelerator.is_main_process:
        logger.info("Saving final model...")
        output_dir = Path(args.output_dir) / args.bird_family
        output_dir.mkdir(parents=True, exist_ok=True)
        unwrapped_unet = accelerator.unwrap_model(unet)
        unwrapped_unet.save_pretrained(output_dir)

        if args.push_to_hub:
            unwrapped_unet.push_to_hub(
                args.hub_model_id or f"chirpneighbors-lora-{args.bird_family}"
            )

    accelerator.end_training()
    logger.info("Training complete!")


if __name__ == "__main__":
    main()
