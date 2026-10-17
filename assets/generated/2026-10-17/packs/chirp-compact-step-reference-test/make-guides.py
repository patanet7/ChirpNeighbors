from pathlib import Path
p=Path(__file__).parent
base=(p.parent/'pose-guide-test/opposite-contact-guide.svg').read_text()
start=base.index('<!-- far leg'); body=base[base.index('<!-- neutral bird body'):base.index('<!-- near leg')]
head='<svg xmlns="http://www.w3.org/2000/svg" width="768" height="512" viewBox="0 0 768 512"><rect width="768" height="512" fill="#f5f2e8"/>'
foot=lambda x,y:f'M{x} {y}l25 2m-25 -2l30 -4m-30 4l22 7m-22 -7l-12 4'
for name,title,far,near,fy,ny,dy in [
 ('compact-step','SHORT STEP: feet clustered under body; near foot lifts slightly', 'M490 373L485 417L492 468','M520 385L512 420L533 455',468,455,0),
 ('compact-opposite-step','SHORT STEP: near foot supports; far foot lifts slightly','M490 373L493 416L510 455','M520 385L512 426L509 468',455,468,0),
 ('light-hop-provisional','PROVISIONAL LIGHT HOP: upright, no deep crouch; not motion-captured','M490 373L488 413L496 458','M520 385L518 422L522 460',458,460,-6)]:
 fx=int(far.split('L')[-1].split()[0]);nx=int(near.split('L')[-1].split()[0]);s=head+f'<text x="18" y="24" font-family="sans-serif" font-size="15">{title}</text><path d="M30 477H744" stroke="#999" stroke-dasharray="6 6"/>'
 s+=f'<g transform="translate(0,{dy})"><g fill="none" stroke="#3378bf" stroke-width="9" stroke-linecap="round"><path d="{far}"/><path d="{foot(fx,fy)}"/></g>'+body+f'<g fill="none" stroke="#ee863a" stroke-width="10" stroke-linecap="round"><path d="{near}"/><path d="{foot(nx,ny)}"/></g></g></svg>'
 (p/(name+'.svg')).write_text(s)
