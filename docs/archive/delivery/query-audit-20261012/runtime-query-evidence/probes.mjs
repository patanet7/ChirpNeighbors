var __defProp = Object.defineProperty;
var __export = (target, all) => {
  for (var name2 in all)
    __defProp(target, name2, { get: all[name2], enumerable: true });
};

// src/lib/scenes/fixture-geometry.ts
var shape = (x, y, width, height, color, alpha) => ({ x, y, width, height, color, ...alpha === void 0 ? {} : { alpha } });
function backgroundPrimitives(setting) {
  const result = [shape(0, 0, 960, 540, "sky"), shape(0, 145, 960, 145, "skyLow")];
  result.push(
    shape(40, 204, 196, 96, "wall"),
    shape(30, 195, 216, 11, "trunk"),
    shape(42, 184, 192, 11, "trunk"),
    shape(60, 173, 156, 11, "wood"),
    shape(73, 218, 44, 38, "sky"),
    shape(93, 218, 4, 38, "wood")
  );
  for (let i = 0; i < 13; i++) {
    const y = 247 - i * 17 % 30;
    result.push(
      shape(i * 80, y, 85, 310 - y, "leaf"),
      shape(i * 80 + 9, y - 8, 61, 10, "leafLight")
    );
  }
  const fenceY = setting === "courtyard" ? 283 : 281;
  result.push(shape(0, fenceY + 21, 960, 9, "wood"), shape(0, fenceY + 58, 960, 8, "wood"));
  for (let x = 0; x < 960; x += 28)
    result.push(shape(x, fenceY, 22, 74, "wood"), shape(x + 3, fenceY + 3, 3, 68, "glow", 0.14));
  return result;
}
function groundPrimitives(setting) {
  const result = [shape(0, 354, 960, 186, "grassLight"), shape(0, 354, 960, 14, "grass")];
  if (setting === "courtyard") {
    result.push(shape(44, 366, 72, 174, "stone"), shape(844, 366, 72, 174, "stone"));
    for (let y = 380; y < 540; y += 28)
      result.push(shape(44, y, 72, 2, "trunk", 0.16), shape(844, y, 72, 2, "trunk", 0.16));
  }
  for (let i = 0; i < 52; i++) {
    const x = 30 + i * 107 % 900, y = 379 + i * 47 % 150;
    result.push(shape(x, y, 3, 5, "grass", 0.65), shape(x + 5, y - 2, 2, 7, "grass", 0.65));
  }
  return result;
}
function foregroundPrimitives() {
  const result = [];
  for (const x of [0, 25, 920, 943])
    result.push(shape(x, 510, 25, 30, "leaf"), shape(x + 5, 501, 17, 12, "leafLight"));
  for (const x of [13, 39, 927, 950])
    result.push(shape(x, 500, 3, 18, "leaf"), shape(x - 4, 497, 11, 7, "flower"));
  return result;
}

// node_modules/zod/v3/external.js
var external_exports = {};
__export(external_exports, {
  BRAND: () => BRAND,
  DIRTY: () => DIRTY,
  EMPTY_PATH: () => EMPTY_PATH,
  INVALID: () => INVALID,
  NEVER: () => NEVER,
  OK: () => OK,
  ParseStatus: () => ParseStatus,
  Schema: () => ZodType,
  ZodAny: () => ZodAny,
  ZodArray: () => ZodArray,
  ZodBigInt: () => ZodBigInt,
  ZodBoolean: () => ZodBoolean,
  ZodBranded: () => ZodBranded,
  ZodCatch: () => ZodCatch,
  ZodDate: () => ZodDate,
  ZodDefault: () => ZodDefault,
  ZodDiscriminatedUnion: () => ZodDiscriminatedUnion,
  ZodEffects: () => ZodEffects,
  ZodEnum: () => ZodEnum,
  ZodError: () => ZodError,
  ZodFirstPartyTypeKind: () => ZodFirstPartyTypeKind,
  ZodFunction: () => ZodFunction,
  ZodIntersection: () => ZodIntersection,
  ZodIssueCode: () => ZodIssueCode,
  ZodLazy: () => ZodLazy,
  ZodLiteral: () => ZodLiteral,
  ZodMap: () => ZodMap,
  ZodNaN: () => ZodNaN,
  ZodNativeEnum: () => ZodNativeEnum,
  ZodNever: () => ZodNever,
  ZodNull: () => ZodNull,
  ZodNullable: () => ZodNullable,
  ZodNumber: () => ZodNumber,
  ZodObject: () => ZodObject,
  ZodOptional: () => ZodOptional,
  ZodParsedType: () => ZodParsedType,
  ZodPipeline: () => ZodPipeline,
  ZodPromise: () => ZodPromise,
  ZodReadonly: () => ZodReadonly,
  ZodRecord: () => ZodRecord,
  ZodSchema: () => ZodType,
  ZodSet: () => ZodSet,
  ZodString: () => ZodString,
  ZodSymbol: () => ZodSymbol,
  ZodTransformer: () => ZodEffects,
  ZodTuple: () => ZodTuple,
  ZodType: () => ZodType,
  ZodUndefined: () => ZodUndefined,
  ZodUnion: () => ZodUnion,
  ZodUnknown: () => ZodUnknown,
  ZodVoid: () => ZodVoid,
  addIssueToContext: () => addIssueToContext,
  any: () => anyType,
  array: () => arrayType,
  bigint: () => bigIntType,
  boolean: () => booleanType,
  coerce: () => coerce,
  custom: () => custom,
  date: () => dateType,
  datetimeRegex: () => datetimeRegex,
  defaultErrorMap: () => en_default,
  discriminatedUnion: () => discriminatedUnionType,
  effect: () => effectsType,
  enum: () => enumType,
  function: () => functionType,
  getErrorMap: () => getErrorMap,
  getParsedType: () => getParsedType,
  instanceof: () => instanceOfType,
  intersection: () => intersectionType,
  isAborted: () => isAborted,
  isAsync: () => isAsync,
  isDirty: () => isDirty,
  isValid: () => isValid,
  late: () => late,
  lazy: () => lazyType,
  literal: () => literalType,
  makeIssue: () => makeIssue,
  map: () => mapType,
  nan: () => nanType,
  nativeEnum: () => nativeEnumType,
  never: () => neverType,
  null: () => nullType,
  nullable: () => nullableType,
  number: () => numberType,
  object: () => objectType,
  objectUtil: () => objectUtil,
  oboolean: () => oboolean,
  onumber: () => onumber,
  optional: () => optionalType,
  ostring: () => ostring,
  pipeline: () => pipelineType,
  preprocess: () => preprocessType,
  promise: () => promiseType,
  quotelessJson: () => quotelessJson,
  record: () => recordType,
  set: () => setType,
  setErrorMap: () => setErrorMap,
  strictObject: () => strictObjectType,
  string: () => stringType,
  symbol: () => symbolType,
  transformer: () => effectsType,
  tuple: () => tupleType,
  undefined: () => undefinedType,
  union: () => unionType,
  unknown: () => unknownType,
  util: () => util,
  void: () => voidType
});

// node_modules/zod/v3/helpers/util.js
var util;
(function(util2) {
  util2.assertEqual = (_) => {
  };
  function assertIs(_arg) {
  }
  util2.assertIs = assertIs;
  function assertNever(_x) {
    throw new Error();
  }
  util2.assertNever = assertNever;
  util2.arrayToEnum = (items) => {
    const obj = {};
    for (const item of items) {
      obj[item] = item;
    }
    return obj;
  };
  util2.getValidEnumValues = (obj) => {
    const validKeys = util2.objectKeys(obj).filter((k) => typeof obj[obj[k]] !== "number");
    const filtered = {};
    for (const k of validKeys) {
      filtered[k] = obj[k];
    }
    return util2.objectValues(filtered);
  };
  util2.objectValues = (obj) => {
    return util2.objectKeys(obj).map(function(e) {
      return obj[e];
    });
  };
  util2.objectKeys = typeof Object.keys === "function" ? (obj) => Object.keys(obj) : (object) => {
    const keys = [];
    for (const key in object) {
      if (Object.prototype.hasOwnProperty.call(object, key)) {
        keys.push(key);
      }
    }
    return keys;
  };
  util2.find = (arr, checker) => {
    for (const item of arr) {
      if (checker(item))
        return item;
    }
    return void 0;
  };
  util2.isInteger = typeof Number.isInteger === "function" ? (val) => Number.isInteger(val) : (val) => typeof val === "number" && Number.isFinite(val) && Math.floor(val) === val;
  function joinValues(array, separator = " | ") {
    return array.map((val) => typeof val === "string" ? `'${val}'` : val).join(separator);
  }
  util2.joinValues = joinValues;
  util2.jsonStringifyReplacer = (_, value) => {
    if (typeof value === "bigint") {
      return value.toString();
    }
    return value;
  };
})(util || (util = {}));
var objectUtil;
(function(objectUtil2) {
  objectUtil2.mergeShapes = (first, second) => {
    return {
      ...first,
      ...second
      // second overwrites first
    };
  };
})(objectUtil || (objectUtil = {}));
var ZodParsedType = util.arrayToEnum([
  "string",
  "nan",
  "number",
  "integer",
  "float",
  "boolean",
  "date",
  "bigint",
  "symbol",
  "function",
  "undefined",
  "null",
  "array",
  "object",
  "unknown",
  "promise",
  "void",
  "never",
  "map",
  "set"
]);
var getParsedType = (data) => {
  const t = typeof data;
  switch (t) {
    case "undefined":
      return ZodParsedType.undefined;
    case "string":
      return ZodParsedType.string;
    case "number":
      return Number.isNaN(data) ? ZodParsedType.nan : ZodParsedType.number;
    case "boolean":
      return ZodParsedType.boolean;
    case "function":
      return ZodParsedType.function;
    case "bigint":
      return ZodParsedType.bigint;
    case "symbol":
      return ZodParsedType.symbol;
    case "object":
      if (Array.isArray(data)) {
        return ZodParsedType.array;
      }
      if (data === null) {
        return ZodParsedType.null;
      }
      if (data.then && typeof data.then === "function" && data.catch && typeof data.catch === "function") {
        return ZodParsedType.promise;
      }
      if (typeof Map !== "undefined" && data instanceof Map) {
        return ZodParsedType.map;
      }
      if (typeof Set !== "undefined" && data instanceof Set) {
        return ZodParsedType.set;
      }
      if (typeof Date !== "undefined" && data instanceof Date) {
        return ZodParsedType.date;
      }
      return ZodParsedType.object;
    default:
      return ZodParsedType.unknown;
  }
};

// node_modules/zod/v3/ZodError.js
var ZodIssueCode = util.arrayToEnum([
  "invalid_type",
  "invalid_literal",
  "custom",
  "invalid_union",
  "invalid_union_discriminator",
  "invalid_enum_value",
  "unrecognized_keys",
  "invalid_arguments",
  "invalid_return_type",
  "invalid_date",
  "invalid_string",
  "too_small",
  "too_big",
  "invalid_intersection_types",
  "not_multiple_of",
  "not_finite"
]);
var quotelessJson = (obj) => {
  const json = JSON.stringify(obj, null, 2);
  return json.replace(/"([^"]+)":/g, "$1:");
};
var ZodError = class _ZodError extends Error {
  get errors() {
    return this.issues;
  }
  constructor(issues) {
    super();
    this.issues = [];
    this.addIssue = (sub) => {
      this.issues = [...this.issues, sub];
    };
    this.addIssues = (subs = []) => {
      this.issues = [...this.issues, ...subs];
    };
    const actualProto = new.target.prototype;
    if (Object.setPrototypeOf) {
      Object.setPrototypeOf(this, actualProto);
    } else {
      this.__proto__ = actualProto;
    }
    this.name = "ZodError";
    this.issues = issues;
  }
  format(_mapper) {
    const mapper = _mapper || function(issue) {
      return issue.message;
    };
    const fieldErrors = { _errors: [] };
    const processError = (error) => {
      for (const issue of error.issues) {
        if (issue.code === "invalid_union") {
          issue.unionErrors.map(processError);
        } else if (issue.code === "invalid_return_type") {
          processError(issue.returnTypeError);
        } else if (issue.code === "invalid_arguments") {
          processError(issue.argumentsError);
        } else if (issue.path.length === 0) {
          fieldErrors._errors.push(mapper(issue));
        } else {
          let curr = fieldErrors;
          let i = 0;
          while (i < issue.path.length) {
            const el = issue.path[i];
            const terminal = i === issue.path.length - 1;
            if (!terminal) {
              curr[el] = curr[el] || { _errors: [] };
            } else {
              curr[el] = curr[el] || { _errors: [] };
              curr[el]._errors.push(mapper(issue));
            }
            curr = curr[el];
            i++;
          }
        }
      }
    };
    processError(this);
    return fieldErrors;
  }
  static assert(value) {
    if (!(value instanceof _ZodError)) {
      throw new Error(`Not a ZodError: ${value}`);
    }
  }
  toString() {
    return this.message;
  }
  get message() {
    return JSON.stringify(this.issues, util.jsonStringifyReplacer, 2);
  }
  get isEmpty() {
    return this.issues.length === 0;
  }
  flatten(mapper = (issue) => issue.message) {
    const fieldErrors = {};
    const formErrors = [];
    for (const sub of this.issues) {
      if (sub.path.length > 0) {
        const firstEl = sub.path[0];
        fieldErrors[firstEl] = fieldErrors[firstEl] || [];
        fieldErrors[firstEl].push(mapper(sub));
      } else {
        formErrors.push(mapper(sub));
      }
    }
    return { formErrors, fieldErrors };
  }
  get formErrors() {
    return this.flatten();
  }
};
ZodError.create = (issues) => {
  const error = new ZodError(issues);
  return error;
};

// node_modules/zod/v3/locales/en.js
var errorMap = (issue, _ctx) => {
  let message;
  switch (issue.code) {
    case ZodIssueCode.invalid_type:
      if (issue.received === ZodParsedType.undefined) {
        message = "Required";
      } else {
        message = `Expected ${issue.expected}, received ${issue.received}`;
      }
      break;
    case ZodIssueCode.invalid_literal:
      message = `Invalid literal value, expected ${JSON.stringify(issue.expected, util.jsonStringifyReplacer)}`;
      break;
    case ZodIssueCode.unrecognized_keys:
      message = `Unrecognized key(s) in object: ${util.joinValues(issue.keys, ", ")}`;
      break;
    case ZodIssueCode.invalid_union:
      message = `Invalid input`;
      break;
    case ZodIssueCode.invalid_union_discriminator:
      message = `Invalid discriminator value. Expected ${util.joinValues(issue.options)}`;
      break;
    case ZodIssueCode.invalid_enum_value:
      message = `Invalid enum value. Expected ${util.joinValues(issue.options)}, received '${issue.received}'`;
      break;
    case ZodIssueCode.invalid_arguments:
      message = `Invalid function arguments`;
      break;
    case ZodIssueCode.invalid_return_type:
      message = `Invalid function return type`;
      break;
    case ZodIssueCode.invalid_date:
      message = `Invalid date`;
      break;
    case ZodIssueCode.invalid_string:
      if (typeof issue.validation === "object") {
        if ("includes" in issue.validation) {
          message = `Invalid input: must include "${issue.validation.includes}"`;
          if (typeof issue.validation.position === "number") {
            message = `${message} at one or more positions greater than or equal to ${issue.validation.position}`;
          }
        } else if ("startsWith" in issue.validation) {
          message = `Invalid input: must start with "${issue.validation.startsWith}"`;
        } else if ("endsWith" in issue.validation) {
          message = `Invalid input: must end with "${issue.validation.endsWith}"`;
        } else {
          util.assertNever(issue.validation);
        }
      } else if (issue.validation !== "regex") {
        message = `Invalid ${issue.validation}`;
      } else {
        message = "Invalid";
      }
      break;
    case ZodIssueCode.too_small:
      if (issue.type === "array")
        message = `Array must contain ${issue.exact ? "exactly" : issue.inclusive ? `at least` : `more than`} ${issue.minimum} element(s)`;
      else if (issue.type === "string")
        message = `String must contain ${issue.exact ? "exactly" : issue.inclusive ? `at least` : `over`} ${issue.minimum} character(s)`;
      else if (issue.type === "number")
        message = `Number must be ${issue.exact ? `exactly equal to ` : issue.inclusive ? `greater than or equal to ` : `greater than `}${issue.minimum}`;
      else if (issue.type === "bigint")
        message = `Number must be ${issue.exact ? `exactly equal to ` : issue.inclusive ? `greater than or equal to ` : `greater than `}${issue.minimum}`;
      else if (issue.type === "date")
        message = `Date must be ${issue.exact ? `exactly equal to ` : issue.inclusive ? `greater than or equal to ` : `greater than `}${new Date(Number(issue.minimum))}`;
      else
        message = "Invalid input";
      break;
    case ZodIssueCode.too_big:
      if (issue.type === "array")
        message = `Array must contain ${issue.exact ? `exactly` : issue.inclusive ? `at most` : `less than`} ${issue.maximum} element(s)`;
      else if (issue.type === "string")
        message = `String must contain ${issue.exact ? `exactly` : issue.inclusive ? `at most` : `under`} ${issue.maximum} character(s)`;
      else if (issue.type === "number")
        message = `Number must be ${issue.exact ? `exactly` : issue.inclusive ? `less than or equal to` : `less than`} ${issue.maximum}`;
      else if (issue.type === "bigint")
        message = `BigInt must be ${issue.exact ? `exactly` : issue.inclusive ? `less than or equal to` : `less than`} ${issue.maximum}`;
      else if (issue.type === "date")
        message = `Date must be ${issue.exact ? `exactly` : issue.inclusive ? `smaller than or equal to` : `smaller than`} ${new Date(Number(issue.maximum))}`;
      else
        message = "Invalid input";
      break;
    case ZodIssueCode.custom:
      message = `Invalid input`;
      break;
    case ZodIssueCode.invalid_intersection_types:
      message = `Intersection results could not be merged`;
      break;
    case ZodIssueCode.not_multiple_of:
      message = `Number must be a multiple of ${issue.multipleOf}`;
      break;
    case ZodIssueCode.not_finite:
      message = "Number must be finite";
      break;
    default:
      message = _ctx.defaultError;
      util.assertNever(issue);
  }
  return { message };
};
var en_default = errorMap;

// node_modules/zod/v3/errors.js
var overrideErrorMap = en_default;
function setErrorMap(map) {
  overrideErrorMap = map;
}
function getErrorMap() {
  return overrideErrorMap;
}

// node_modules/zod/v3/helpers/parseUtil.js
var makeIssue = (params) => {
  const { data, path, errorMaps, issueData } = params;
  const fullPath = [...path, ...issueData.path || []];
  const fullIssue = {
    ...issueData,
    path: fullPath
  };
  if (issueData.message !== void 0) {
    return {
      ...issueData,
      path: fullPath,
      message: issueData.message
    };
  }
  let errorMessage = "";
  const maps = errorMaps.filter((m) => !!m).slice().reverse();
  for (const map of maps) {
    errorMessage = map(fullIssue, { data, defaultError: errorMessage }).message;
  }
  return {
    ...issueData,
    path: fullPath,
    message: errorMessage
  };
};
var EMPTY_PATH = [];
function addIssueToContext(ctx, issueData) {
  const overrideMap = getErrorMap();
  const issue = makeIssue({
    issueData,
    data: ctx.data,
    path: ctx.path,
    errorMaps: [
      ctx.common.contextualErrorMap,
      // contextual error map is first priority
      ctx.schemaErrorMap,
      // then schema-bound map if available
      overrideMap,
      // then global override map
      overrideMap === en_default ? void 0 : en_default
      // then global default map
    ].filter((x) => !!x)
  });
  ctx.common.issues.push(issue);
}
var ParseStatus = class _ParseStatus {
  constructor() {
    this.value = "valid";
  }
  dirty() {
    if (this.value === "valid")
      this.value = "dirty";
  }
  abort() {
    if (this.value !== "aborted")
      this.value = "aborted";
  }
  static mergeArray(status, results) {
    const arrayValue = [];
    for (const s of results) {
      if (s.status === "aborted")
        return INVALID;
      if (s.status === "dirty")
        status.dirty();
      arrayValue.push(s.value);
    }
    return { status: status.value, value: arrayValue };
  }
  static async mergeObjectAsync(status, pairs) {
    const syncPairs = [];
    for (const pair of pairs) {
      const key = await pair.key;
      const value = await pair.value;
      syncPairs.push({
        key,
        value
      });
    }
    return _ParseStatus.mergeObjectSync(status, syncPairs);
  }
  static mergeObjectSync(status, pairs) {
    const finalObject = {};
    for (const pair of pairs) {
      const { key, value } = pair;
      if (key.status === "aborted")
        return INVALID;
      if (value.status === "aborted")
        return INVALID;
      if (key.status === "dirty")
        status.dirty();
      if (value.status === "dirty")
        status.dirty();
      if (key.value !== "__proto__" && (typeof value.value !== "undefined" || pair.alwaysSet)) {
        finalObject[key.value] = value.value;
      }
    }
    return { status: status.value, value: finalObject };
  }
};
var INVALID = Object.freeze({
  status: "aborted"
});
var DIRTY = (value) => ({ status: "dirty", value });
var OK = (value) => ({ status: "valid", value });
var isAborted = (x) => x.status === "aborted";
var isDirty = (x) => x.status === "dirty";
var isValid = (x) => x.status === "valid";
var isAsync = (x) => typeof Promise !== "undefined" && x instanceof Promise;

// node_modules/zod/v3/helpers/errorUtil.js
var errorUtil;
(function(errorUtil2) {
  errorUtil2.errToObj = (message) => typeof message === "string" ? { message } : message || {};
  errorUtil2.toString = (message) => typeof message === "string" ? message : message?.message;
})(errorUtil || (errorUtil = {}));

// node_modules/zod/v3/types.js
var ParseInputLazyPath = class {
  constructor(parent, value, path, key) {
    this._cachedPath = [];
    this.parent = parent;
    this.data = value;
    this._path = path;
    this._key = key;
  }
  get path() {
    if (!this._cachedPath.length) {
      if (Array.isArray(this._key)) {
        this._cachedPath.push(...this._path, ...this._key);
      } else {
        this._cachedPath.push(...this._path, this._key);
      }
    }
    return this._cachedPath;
  }
};
var handleResult = (ctx, result) => {
  if (isValid(result)) {
    return { success: true, data: result.value };
  } else {
    if (!ctx.common.issues.length) {
      throw new Error("Validation failed but no issues detected.");
    }
    return {
      success: false,
      get error() {
        if (this._error)
          return this._error;
        const error = new ZodError(ctx.common.issues);
        this._error = error;
        return this._error;
      }
    };
  }
};
function processCreateParams(params) {
  if (!params)
    return {};
  const { errorMap: errorMap2, invalid_type_error, required_error, description } = params;
  if (errorMap2 && (invalid_type_error || required_error)) {
    throw new Error(`Can't use "invalid_type_error" or "required_error" in conjunction with custom error map.`);
  }
  if (errorMap2)
    return { errorMap: errorMap2, description };
  const customMap = (iss, ctx) => {
    const { message } = params;
    if (iss.code === "invalid_enum_value") {
      return { message: message ?? ctx.defaultError };
    }
    if (typeof ctx.data === "undefined") {
      return { message: message ?? required_error ?? ctx.defaultError };
    }
    if (iss.code !== "invalid_type")
      return { message: ctx.defaultError };
    return { message: message ?? invalid_type_error ?? ctx.defaultError };
  };
  return { errorMap: customMap, description };
}
var ZodType = class {
  get description() {
    return this._def.description;
  }
  _getType(input) {
    return getParsedType(input.data);
  }
  _getOrReturnCtx(input, ctx) {
    return ctx || {
      common: input.parent.common,
      data: input.data,
      parsedType: getParsedType(input.data),
      schemaErrorMap: this._def.errorMap,
      path: input.path,
      parent: input.parent
    };
  }
  _processInputParams(input) {
    return {
      status: new ParseStatus(),
      ctx: {
        common: input.parent.common,
        data: input.data,
        parsedType: getParsedType(input.data),
        schemaErrorMap: this._def.errorMap,
        path: input.path,
        parent: input.parent
      }
    };
  }
  _parseSync(input) {
    const result = this._parse(input);
    if (isAsync(result)) {
      throw new Error("Synchronous parse encountered promise.");
    }
    return result;
  }
  _parseAsync(input) {
    const result = this._parse(input);
    return Promise.resolve(result);
  }
  parse(data, params) {
    const result = this.safeParse(data, params);
    if (result.success)
      return result.data;
    throw result.error;
  }
  safeParse(data, params) {
    const ctx = {
      common: {
        issues: [],
        async: params?.async ?? false,
        contextualErrorMap: params?.errorMap
      },
      path: params?.path || [],
      schemaErrorMap: this._def.errorMap,
      parent: null,
      data,
      parsedType: getParsedType(data)
    };
    const result = this._parseSync({ data, path: ctx.path, parent: ctx });
    return handleResult(ctx, result);
  }
  "~validate"(data) {
    const ctx = {
      common: {
        issues: [],
        async: !!this["~standard"].async
      },
      path: [],
      schemaErrorMap: this._def.errorMap,
      parent: null,
      data,
      parsedType: getParsedType(data)
    };
    if (!this["~standard"].async) {
      try {
        const result = this._parseSync({ data, path: [], parent: ctx });
        return isValid(result) ? {
          value: result.value
        } : {
          issues: ctx.common.issues
        };
      } catch (err) {
        if (err?.message?.toLowerCase()?.includes("encountered")) {
          this["~standard"].async = true;
        }
        ctx.common = {
          issues: [],
          async: true
        };
      }
    }
    return this._parseAsync({ data, path: [], parent: ctx }).then((result) => isValid(result) ? {
      value: result.value
    } : {
      issues: ctx.common.issues
    });
  }
  async parseAsync(data, params) {
    const result = await this.safeParseAsync(data, params);
    if (result.success)
      return result.data;
    throw result.error;
  }
  async safeParseAsync(data, params) {
    const ctx = {
      common: {
        issues: [],
        contextualErrorMap: params?.errorMap,
        async: true
      },
      path: params?.path || [],
      schemaErrorMap: this._def.errorMap,
      parent: null,
      data,
      parsedType: getParsedType(data)
    };
    const maybeAsyncResult = this._parse({ data, path: ctx.path, parent: ctx });
    const result = await (isAsync(maybeAsyncResult) ? maybeAsyncResult : Promise.resolve(maybeAsyncResult));
    return handleResult(ctx, result);
  }
  refine(check, message) {
    const getIssueProperties = (val) => {
      if (typeof message === "string" || typeof message === "undefined") {
        return { message };
      } else if (typeof message === "function") {
        return message(val);
      } else {
        return message;
      }
    };
    return this._refinement((val, ctx) => {
      const result = check(val);
      const setError = () => ctx.addIssue({
        code: ZodIssueCode.custom,
        ...getIssueProperties(val)
      });
      if (typeof Promise !== "undefined" && result instanceof Promise) {
        return result.then((data) => {
          if (!data) {
            setError();
            return false;
          } else {
            return true;
          }
        });
      }
      if (!result) {
        setError();
        return false;
      } else {
        return true;
      }
    });
  }
  refinement(check, refinementData) {
    return this._refinement((val, ctx) => {
      if (!check(val)) {
        ctx.addIssue(typeof refinementData === "function" ? refinementData(val, ctx) : refinementData);
        return false;
      } else {
        return true;
      }
    });
  }
  _refinement(refinement) {
    return new ZodEffects({
      schema: this,
      typeName: ZodFirstPartyTypeKind.ZodEffects,
      effect: { type: "refinement", refinement }
    });
  }
  superRefine(refinement) {
    return this._refinement(refinement);
  }
  constructor(def) {
    this.spa = this.safeParseAsync;
    this._def = def;
    this.parse = this.parse.bind(this);
    this.safeParse = this.safeParse.bind(this);
    this.parseAsync = this.parseAsync.bind(this);
    this.safeParseAsync = this.safeParseAsync.bind(this);
    this.spa = this.spa.bind(this);
    this.refine = this.refine.bind(this);
    this.refinement = this.refinement.bind(this);
    this.superRefine = this.superRefine.bind(this);
    this.optional = this.optional.bind(this);
    this.nullable = this.nullable.bind(this);
    this.nullish = this.nullish.bind(this);
    this.array = this.array.bind(this);
    this.promise = this.promise.bind(this);
    this.or = this.or.bind(this);
    this.and = this.and.bind(this);
    this.transform = this.transform.bind(this);
    this.brand = this.brand.bind(this);
    this.default = this.default.bind(this);
    this.catch = this.catch.bind(this);
    this.describe = this.describe.bind(this);
    this.pipe = this.pipe.bind(this);
    this.readonly = this.readonly.bind(this);
    this.isNullable = this.isNullable.bind(this);
    this.isOptional = this.isOptional.bind(this);
    this["~standard"] = {
      version: 1,
      vendor: "zod",
      validate: (data) => this["~validate"](data)
    };
  }
  optional() {
    return ZodOptional.create(this, this._def);
  }
  nullable() {
    return ZodNullable.create(this, this._def);
  }
  nullish() {
    return this.nullable().optional();
  }
  array() {
    return ZodArray.create(this);
  }
  promise() {
    return ZodPromise.create(this, this._def);
  }
  or(option) {
    return ZodUnion.create([this, option], this._def);
  }
  and(incoming) {
    return ZodIntersection.create(this, incoming, this._def);
  }
  transform(transform) {
    return new ZodEffects({
      ...processCreateParams(this._def),
      schema: this,
      typeName: ZodFirstPartyTypeKind.ZodEffects,
      effect: { type: "transform", transform }
    });
  }
  default(def) {
    const defaultValueFunc = typeof def === "function" ? def : () => def;
    return new ZodDefault({
      ...processCreateParams(this._def),
      innerType: this,
      defaultValue: defaultValueFunc,
      typeName: ZodFirstPartyTypeKind.ZodDefault
    });
  }
  brand() {
    return new ZodBranded({
      typeName: ZodFirstPartyTypeKind.ZodBranded,
      type: this,
      ...processCreateParams(this._def)
    });
  }
  catch(def) {
    const catchValueFunc = typeof def === "function" ? def : () => def;
    return new ZodCatch({
      ...processCreateParams(this._def),
      innerType: this,
      catchValue: catchValueFunc,
      typeName: ZodFirstPartyTypeKind.ZodCatch
    });
  }
  describe(description) {
    const This = this.constructor;
    return new This({
      ...this._def,
      description
    });
  }
  pipe(target) {
    return ZodPipeline.create(this, target);
  }
  readonly() {
    return ZodReadonly.create(this);
  }
  isOptional() {
    return this.safeParse(void 0).success;
  }
  isNullable() {
    return this.safeParse(null).success;
  }
};
var cuidRegex = /^c[^\s-]{8,}$/i;
var cuid2Regex = /^[0-9a-z]+$/;
var ulidRegex = /^[0-9A-HJKMNP-TV-Z]{26}$/i;
var uuidRegex = /^[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}$/i;
var nanoidRegex = /^[a-z0-9_-]{21}$/i;
var jwtRegex = /^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]*$/;
var durationRegex = /^[-+]?P(?!$)(?:(?:[-+]?\d+Y)|(?:[-+]?\d+[.,]\d+Y$))?(?:(?:[-+]?\d+M)|(?:[-+]?\d+[.,]\d+M$))?(?:(?:[-+]?\d+W)|(?:[-+]?\d+[.,]\d+W$))?(?:(?:[-+]?\d+D)|(?:[-+]?\d+[.,]\d+D$))?(?:T(?=[\d+-])(?:(?:[-+]?\d+H)|(?:[-+]?\d+[.,]\d+H$))?(?:(?:[-+]?\d+M)|(?:[-+]?\d+[.,]\d+M$))?(?:[-+]?\d+(?:[.,]\d+)?S)?)??$/;
var emailRegex = /^(?!\.)(?!.*\.\.)([A-Z0-9_'+\-\.]*)[A-Z0-9_+-]@([A-Z0-9][A-Z0-9\-]*\.)+[A-Z]{2,}$/i;
var _emojiRegex = `^(\\p{Extended_Pictographic}|\\p{Emoji_Component})+$`;
var emojiRegex;
var ipv4Regex = /^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])$/;
var ipv4CidrRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\/(3[0-2]|[12]?[0-9])$/;
var ipv6Regex = /^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$/;
var ipv6CidrRegex = /^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))\/(12[0-8]|1[01][0-9]|[1-9]?[0-9])$/;
var base64Regex = /^([0-9a-zA-Z+/]{4})*(([0-9a-zA-Z+/]{2}==)|([0-9a-zA-Z+/]{3}=))?$/;
var base64urlRegex = /^([0-9a-zA-Z-_]{4})*(([0-9a-zA-Z-_]{2}(==)?)|([0-9a-zA-Z-_]{3}(=)?))?$/;
var dateRegexSource = `((\\d\\d[2468][048]|\\d\\d[13579][26]|\\d\\d0[48]|[02468][048]00|[13579][26]00)-02-29|\\d{4}-((0[13578]|1[02])-(0[1-9]|[12]\\d|3[01])|(0[469]|11)-(0[1-9]|[12]\\d|30)|(02)-(0[1-9]|1\\d|2[0-8])))`;
var dateRegex = new RegExp(`^${dateRegexSource}$`);
function timeRegexSource(args) {
  let secondsRegexSource = `[0-5]\\d`;
  if (args.precision) {
    secondsRegexSource = `${secondsRegexSource}\\.\\d{${args.precision}}`;
  } else if (args.precision == null) {
    secondsRegexSource = `${secondsRegexSource}(\\.\\d+)?`;
  }
  const secondsQuantifier = args.precision ? "+" : "?";
  return `([01]\\d|2[0-3]):[0-5]\\d(:${secondsRegexSource})${secondsQuantifier}`;
}
function timeRegex(args) {
  return new RegExp(`^${timeRegexSource(args)}$`);
}
function datetimeRegex(args) {
  let regex = `${dateRegexSource}T${timeRegexSource(args)}`;
  const opts = [];
  opts.push(args.local ? `Z?` : `Z`);
  if (args.offset)
    opts.push(`([+-]\\d{2}:?\\d{2})`);
  regex = `${regex}(${opts.join("|")})`;
  return new RegExp(`^${regex}$`);
}
function isValidIP(ip, version2) {
  if ((version2 === "v4" || !version2) && ipv4Regex.test(ip)) {
    return true;
  }
  if ((version2 === "v6" || !version2) && ipv6Regex.test(ip)) {
    return true;
  }
  return false;
}
function isValidJWT(jwt, alg) {
  if (!jwtRegex.test(jwt))
    return false;
  try {
    const [header] = jwt.split(".");
    if (!header)
      return false;
    const base64 = header.replace(/-/g, "+").replace(/_/g, "/").padEnd(header.length + (4 - header.length % 4) % 4, "=");
    const decoded = JSON.parse(atob(base64));
    if (typeof decoded !== "object" || decoded === null)
      return false;
    if ("typ" in decoded && decoded?.typ !== "JWT")
      return false;
    if (!decoded.alg)
      return false;
    if (alg && decoded.alg !== alg)
      return false;
    return true;
  } catch {
    return false;
  }
}
function isValidCidr(ip, version2) {
  if ((version2 === "v4" || !version2) && ipv4CidrRegex.test(ip)) {
    return true;
  }
  if ((version2 === "v6" || !version2) && ipv6CidrRegex.test(ip)) {
    return true;
  }
  return false;
}
var ZodString = class _ZodString extends ZodType {
  _parse(input) {
    if (this._def.coerce) {
      input.data = String(input.data);
    }
    const parsedType = this._getType(input);
    if (parsedType !== ZodParsedType.string) {
      const ctx2 = this._getOrReturnCtx(input);
      addIssueToContext(ctx2, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.string,
        received: ctx2.parsedType
      });
      return INVALID;
    }
    const status = new ParseStatus();
    let ctx = void 0;
    for (const check of this._def.checks) {
      if (check.kind === "min") {
        if (input.data.length < check.value) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.too_small,
            minimum: check.value,
            type: "string",
            inclusive: true,
            exact: false,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "max") {
        if (input.data.length > check.value) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.too_big,
            maximum: check.value,
            type: "string",
            inclusive: true,
            exact: false,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "length") {
        const tooBig = input.data.length > check.value;
        const tooSmall = input.data.length < check.value;
        if (tooBig || tooSmall) {
          ctx = this._getOrReturnCtx(input, ctx);
          if (tooBig) {
            addIssueToContext(ctx, {
              code: ZodIssueCode.too_big,
              maximum: check.value,
              type: "string",
              inclusive: true,
              exact: true,
              message: check.message
            });
          } else if (tooSmall) {
            addIssueToContext(ctx, {
              code: ZodIssueCode.too_small,
              minimum: check.value,
              type: "string",
              inclusive: true,
              exact: true,
              message: check.message
            });
          }
          status.dirty();
        }
      } else if (check.kind === "email") {
        if (!emailRegex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "email",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "emoji") {
        if (!emojiRegex) {
          emojiRegex = new RegExp(_emojiRegex, "u");
        }
        if (!emojiRegex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "emoji",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "uuid") {
        if (!uuidRegex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "uuid",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "nanoid") {
        if (!nanoidRegex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "nanoid",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "cuid") {
        if (!cuidRegex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "cuid",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "cuid2") {
        if (!cuid2Regex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "cuid2",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "ulid") {
        if (!ulidRegex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "ulid",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "url") {
        try {
          new URL(input.data);
        } catch {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "url",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "regex") {
        check.regex.lastIndex = 0;
        const testResult = check.regex.test(input.data);
        if (!testResult) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "regex",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "trim") {
        input.data = input.data.trim();
      } else if (check.kind === "includes") {
        if (!input.data.includes(check.value, check.position)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.invalid_string,
            validation: { includes: check.value, position: check.position },
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "toLowerCase") {
        input.data = input.data.toLowerCase();
      } else if (check.kind === "toUpperCase") {
        input.data = input.data.toUpperCase();
      } else if (check.kind === "startsWith") {
        if (!input.data.startsWith(check.value)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.invalid_string,
            validation: { startsWith: check.value },
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "endsWith") {
        if (!input.data.endsWith(check.value)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.invalid_string,
            validation: { endsWith: check.value },
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "datetime") {
        const regex = datetimeRegex(check);
        if (!regex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.invalid_string,
            validation: "datetime",
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "date") {
        const regex = dateRegex;
        if (!regex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.invalid_string,
            validation: "date",
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "time") {
        const regex = timeRegex(check);
        if (!regex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.invalid_string,
            validation: "time",
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "duration") {
        if (!durationRegex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "duration",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "ip") {
        if (!isValidIP(input.data, check.version)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "ip",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "jwt") {
        if (!isValidJWT(input.data, check.alg)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "jwt",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "cidr") {
        if (!isValidCidr(input.data, check.version)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "cidr",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "base64") {
        if (!base64Regex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "base64",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "base64url") {
        if (!base64urlRegex.test(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            validation: "base64url",
            code: ZodIssueCode.invalid_string,
            message: check.message
          });
          status.dirty();
        }
      } else {
        util.assertNever(check);
      }
    }
    return { status: status.value, value: input.data };
  }
  _regex(regex, validation, message) {
    return this.refinement((data) => regex.test(data), {
      validation,
      code: ZodIssueCode.invalid_string,
      ...errorUtil.errToObj(message)
    });
  }
  _addCheck(check) {
    return new _ZodString({
      ...this._def,
      checks: [...this._def.checks, check]
    });
  }
  email(message) {
    return this._addCheck({ kind: "email", ...errorUtil.errToObj(message) });
  }
  url(message) {
    return this._addCheck({ kind: "url", ...errorUtil.errToObj(message) });
  }
  emoji(message) {
    return this._addCheck({ kind: "emoji", ...errorUtil.errToObj(message) });
  }
  uuid(message) {
    return this._addCheck({ kind: "uuid", ...errorUtil.errToObj(message) });
  }
  nanoid(message) {
    return this._addCheck({ kind: "nanoid", ...errorUtil.errToObj(message) });
  }
  cuid(message) {
    return this._addCheck({ kind: "cuid", ...errorUtil.errToObj(message) });
  }
  cuid2(message) {
    return this._addCheck({ kind: "cuid2", ...errorUtil.errToObj(message) });
  }
  ulid(message) {
    return this._addCheck({ kind: "ulid", ...errorUtil.errToObj(message) });
  }
  base64(message) {
    return this._addCheck({ kind: "base64", ...errorUtil.errToObj(message) });
  }
  base64url(message) {
    return this._addCheck({
      kind: "base64url",
      ...errorUtil.errToObj(message)
    });
  }
  jwt(options) {
    return this._addCheck({ kind: "jwt", ...errorUtil.errToObj(options) });
  }
  ip(options) {
    return this._addCheck({ kind: "ip", ...errorUtil.errToObj(options) });
  }
  cidr(options) {
    return this._addCheck({ kind: "cidr", ...errorUtil.errToObj(options) });
  }
  datetime(options) {
    if (typeof options === "string") {
      return this._addCheck({
        kind: "datetime",
        precision: null,
        offset: false,
        local: false,
        message: options
      });
    }
    return this._addCheck({
      kind: "datetime",
      precision: typeof options?.precision === "undefined" ? null : options?.precision,
      offset: options?.offset ?? false,
      local: options?.local ?? false,
      ...errorUtil.errToObj(options?.message)
    });
  }
  date(message) {
    return this._addCheck({ kind: "date", message });
  }
  time(options) {
    if (typeof options === "string") {
      return this._addCheck({
        kind: "time",
        precision: null,
        message: options
      });
    }
    return this._addCheck({
      kind: "time",
      precision: typeof options?.precision === "undefined" ? null : options?.precision,
      ...errorUtil.errToObj(options?.message)
    });
  }
  duration(message) {
    return this._addCheck({ kind: "duration", ...errorUtil.errToObj(message) });
  }
  regex(regex, message) {
    return this._addCheck({
      kind: "regex",
      regex,
      ...errorUtil.errToObj(message)
    });
  }
  includes(value, options) {
    return this._addCheck({
      kind: "includes",
      value,
      position: options?.position,
      ...errorUtil.errToObj(options?.message)
    });
  }
  startsWith(value, message) {
    return this._addCheck({
      kind: "startsWith",
      value,
      ...errorUtil.errToObj(message)
    });
  }
  endsWith(value, message) {
    return this._addCheck({
      kind: "endsWith",
      value,
      ...errorUtil.errToObj(message)
    });
  }
  min(minLength, message) {
    return this._addCheck({
      kind: "min",
      value: minLength,
      ...errorUtil.errToObj(message)
    });
  }
  max(maxLength, message) {
    return this._addCheck({
      kind: "max",
      value: maxLength,
      ...errorUtil.errToObj(message)
    });
  }
  length(len, message) {
    return this._addCheck({
      kind: "length",
      value: len,
      ...errorUtil.errToObj(message)
    });
  }
  /**
   * Equivalent to `.min(1)`
   */
  nonempty(message) {
    return this.min(1, errorUtil.errToObj(message));
  }
  trim() {
    return new _ZodString({
      ...this._def,
      checks: [...this._def.checks, { kind: "trim" }]
    });
  }
  toLowerCase() {
    return new _ZodString({
      ...this._def,
      checks: [...this._def.checks, { kind: "toLowerCase" }]
    });
  }
  toUpperCase() {
    return new _ZodString({
      ...this._def,
      checks: [...this._def.checks, { kind: "toUpperCase" }]
    });
  }
  get isDatetime() {
    return !!this._def.checks.find((ch) => ch.kind === "datetime");
  }
  get isDate() {
    return !!this._def.checks.find((ch) => ch.kind === "date");
  }
  get isTime() {
    return !!this._def.checks.find((ch) => ch.kind === "time");
  }
  get isDuration() {
    return !!this._def.checks.find((ch) => ch.kind === "duration");
  }
  get isEmail() {
    return !!this._def.checks.find((ch) => ch.kind === "email");
  }
  get isURL() {
    return !!this._def.checks.find((ch) => ch.kind === "url");
  }
  get isEmoji() {
    return !!this._def.checks.find((ch) => ch.kind === "emoji");
  }
  get isUUID() {
    return !!this._def.checks.find((ch) => ch.kind === "uuid");
  }
  get isNANOID() {
    return !!this._def.checks.find((ch) => ch.kind === "nanoid");
  }
  get isCUID() {
    return !!this._def.checks.find((ch) => ch.kind === "cuid");
  }
  get isCUID2() {
    return !!this._def.checks.find((ch) => ch.kind === "cuid2");
  }
  get isULID() {
    return !!this._def.checks.find((ch) => ch.kind === "ulid");
  }
  get isIP() {
    return !!this._def.checks.find((ch) => ch.kind === "ip");
  }
  get isCIDR() {
    return !!this._def.checks.find((ch) => ch.kind === "cidr");
  }
  get isBase64() {
    return !!this._def.checks.find((ch) => ch.kind === "base64");
  }
  get isBase64url() {
    return !!this._def.checks.find((ch) => ch.kind === "base64url");
  }
  get minLength() {
    let min = null;
    for (const ch of this._def.checks) {
      if (ch.kind === "min") {
        if (min === null || ch.value > min)
          min = ch.value;
      }
    }
    return min;
  }
  get maxLength() {
    let max = null;
    for (const ch of this._def.checks) {
      if (ch.kind === "max") {
        if (max === null || ch.value < max)
          max = ch.value;
      }
    }
    return max;
  }
};
ZodString.create = (params) => {
  return new ZodString({
    checks: [],
    typeName: ZodFirstPartyTypeKind.ZodString,
    coerce: params?.coerce ?? false,
    ...processCreateParams(params)
  });
};
function floatSafeRemainder(val, step) {
  const valDecCount = (val.toString().split(".")[1] || "").length;
  const stepDecCount = (step.toString().split(".")[1] || "").length;
  const decCount = valDecCount > stepDecCount ? valDecCount : stepDecCount;
  const valInt = Number.parseInt(val.toFixed(decCount).replace(".", ""));
  const stepInt = Number.parseInt(step.toFixed(decCount).replace(".", ""));
  return valInt % stepInt / 10 ** decCount;
}
var ZodNumber = class _ZodNumber extends ZodType {
  constructor() {
    super(...arguments);
    this.min = this.gte;
    this.max = this.lte;
    this.step = this.multipleOf;
  }
  _parse(input) {
    if (this._def.coerce) {
      input.data = Number(input.data);
    }
    const parsedType = this._getType(input);
    if (parsedType !== ZodParsedType.number) {
      const ctx2 = this._getOrReturnCtx(input);
      addIssueToContext(ctx2, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.number,
        received: ctx2.parsedType
      });
      return INVALID;
    }
    let ctx = void 0;
    const status = new ParseStatus();
    for (const check of this._def.checks) {
      if (check.kind === "int") {
        if (!util.isInteger(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.invalid_type,
            expected: "integer",
            received: "float",
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "min") {
        const tooSmall = check.inclusive ? input.data < check.value : input.data <= check.value;
        if (tooSmall) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.too_small,
            minimum: check.value,
            type: "number",
            inclusive: check.inclusive,
            exact: false,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "max") {
        const tooBig = check.inclusive ? input.data > check.value : input.data >= check.value;
        if (tooBig) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.too_big,
            maximum: check.value,
            type: "number",
            inclusive: check.inclusive,
            exact: false,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "multipleOf") {
        if (floatSafeRemainder(input.data, check.value) !== 0) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.not_multiple_of,
            multipleOf: check.value,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "finite") {
        if (!Number.isFinite(input.data)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.not_finite,
            message: check.message
          });
          status.dirty();
        }
      } else {
        util.assertNever(check);
      }
    }
    return { status: status.value, value: input.data };
  }
  gte(value, message) {
    return this.setLimit("min", value, true, errorUtil.toString(message));
  }
  gt(value, message) {
    return this.setLimit("min", value, false, errorUtil.toString(message));
  }
  lte(value, message) {
    return this.setLimit("max", value, true, errorUtil.toString(message));
  }
  lt(value, message) {
    return this.setLimit("max", value, false, errorUtil.toString(message));
  }
  setLimit(kind, value, inclusive, message) {
    return new _ZodNumber({
      ...this._def,
      checks: [
        ...this._def.checks,
        {
          kind,
          value,
          inclusive,
          message: errorUtil.toString(message)
        }
      ]
    });
  }
  _addCheck(check) {
    return new _ZodNumber({
      ...this._def,
      checks: [...this._def.checks, check]
    });
  }
  int(message) {
    return this._addCheck({
      kind: "int",
      message: errorUtil.toString(message)
    });
  }
  positive(message) {
    return this._addCheck({
      kind: "min",
      value: 0,
      inclusive: false,
      message: errorUtil.toString(message)
    });
  }
  negative(message) {
    return this._addCheck({
      kind: "max",
      value: 0,
      inclusive: false,
      message: errorUtil.toString(message)
    });
  }
  nonpositive(message) {
    return this._addCheck({
      kind: "max",
      value: 0,
      inclusive: true,
      message: errorUtil.toString(message)
    });
  }
  nonnegative(message) {
    return this._addCheck({
      kind: "min",
      value: 0,
      inclusive: true,
      message: errorUtil.toString(message)
    });
  }
  multipleOf(value, message) {
    return this._addCheck({
      kind: "multipleOf",
      value,
      message: errorUtil.toString(message)
    });
  }
  finite(message) {
    return this._addCheck({
      kind: "finite",
      message: errorUtil.toString(message)
    });
  }
  safe(message) {
    return this._addCheck({
      kind: "min",
      inclusive: true,
      value: Number.MIN_SAFE_INTEGER,
      message: errorUtil.toString(message)
    })._addCheck({
      kind: "max",
      inclusive: true,
      value: Number.MAX_SAFE_INTEGER,
      message: errorUtil.toString(message)
    });
  }
  get minValue() {
    let min = null;
    for (const ch of this._def.checks) {
      if (ch.kind === "min") {
        if (min === null || ch.value > min)
          min = ch.value;
      }
    }
    return min;
  }
  get maxValue() {
    let max = null;
    for (const ch of this._def.checks) {
      if (ch.kind === "max") {
        if (max === null || ch.value < max)
          max = ch.value;
      }
    }
    return max;
  }
  get isInt() {
    return !!this._def.checks.find((ch) => ch.kind === "int" || ch.kind === "multipleOf" && util.isInteger(ch.value));
  }
  get isFinite() {
    let max = null;
    let min = null;
    for (const ch of this._def.checks) {
      if (ch.kind === "finite" || ch.kind === "int" || ch.kind === "multipleOf") {
        return true;
      } else if (ch.kind === "min") {
        if (min === null || ch.value > min)
          min = ch.value;
      } else if (ch.kind === "max") {
        if (max === null || ch.value < max)
          max = ch.value;
      }
    }
    return Number.isFinite(min) && Number.isFinite(max);
  }
};
ZodNumber.create = (params) => {
  return new ZodNumber({
    checks: [],
    typeName: ZodFirstPartyTypeKind.ZodNumber,
    coerce: params?.coerce || false,
    ...processCreateParams(params)
  });
};
var ZodBigInt = class _ZodBigInt extends ZodType {
  constructor() {
    super(...arguments);
    this.min = this.gte;
    this.max = this.lte;
  }
  _parse(input) {
    if (this._def.coerce) {
      try {
        input.data = BigInt(input.data);
      } catch {
        return this._getInvalidInput(input);
      }
    }
    const parsedType = this._getType(input);
    if (parsedType !== ZodParsedType.bigint) {
      return this._getInvalidInput(input);
    }
    let ctx = void 0;
    const status = new ParseStatus();
    for (const check of this._def.checks) {
      if (check.kind === "min") {
        const tooSmall = check.inclusive ? input.data < check.value : input.data <= check.value;
        if (tooSmall) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.too_small,
            type: "bigint",
            minimum: check.value,
            inclusive: check.inclusive,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "max") {
        const tooBig = check.inclusive ? input.data > check.value : input.data >= check.value;
        if (tooBig) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.too_big,
            type: "bigint",
            maximum: check.value,
            inclusive: check.inclusive,
            message: check.message
          });
          status.dirty();
        }
      } else if (check.kind === "multipleOf") {
        if (input.data % check.value !== BigInt(0)) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.not_multiple_of,
            multipleOf: check.value,
            message: check.message
          });
          status.dirty();
        }
      } else {
        util.assertNever(check);
      }
    }
    return { status: status.value, value: input.data };
  }
  _getInvalidInput(input) {
    const ctx = this._getOrReturnCtx(input);
    addIssueToContext(ctx, {
      code: ZodIssueCode.invalid_type,
      expected: ZodParsedType.bigint,
      received: ctx.parsedType
    });
    return INVALID;
  }
  gte(value, message) {
    return this.setLimit("min", value, true, errorUtil.toString(message));
  }
  gt(value, message) {
    return this.setLimit("min", value, false, errorUtil.toString(message));
  }
  lte(value, message) {
    return this.setLimit("max", value, true, errorUtil.toString(message));
  }
  lt(value, message) {
    return this.setLimit("max", value, false, errorUtil.toString(message));
  }
  setLimit(kind, value, inclusive, message) {
    return new _ZodBigInt({
      ...this._def,
      checks: [
        ...this._def.checks,
        {
          kind,
          value,
          inclusive,
          message: errorUtil.toString(message)
        }
      ]
    });
  }
  _addCheck(check) {
    return new _ZodBigInt({
      ...this._def,
      checks: [...this._def.checks, check]
    });
  }
  positive(message) {
    return this._addCheck({
      kind: "min",
      value: BigInt(0),
      inclusive: false,
      message: errorUtil.toString(message)
    });
  }
  negative(message) {
    return this._addCheck({
      kind: "max",
      value: BigInt(0),
      inclusive: false,
      message: errorUtil.toString(message)
    });
  }
  nonpositive(message) {
    return this._addCheck({
      kind: "max",
      value: BigInt(0),
      inclusive: true,
      message: errorUtil.toString(message)
    });
  }
  nonnegative(message) {
    return this._addCheck({
      kind: "min",
      value: BigInt(0),
      inclusive: true,
      message: errorUtil.toString(message)
    });
  }
  multipleOf(value, message) {
    return this._addCheck({
      kind: "multipleOf",
      value,
      message: errorUtil.toString(message)
    });
  }
  get minValue() {
    let min = null;
    for (const ch of this._def.checks) {
      if (ch.kind === "min") {
        if (min === null || ch.value > min)
          min = ch.value;
      }
    }
    return min;
  }
  get maxValue() {
    let max = null;
    for (const ch of this._def.checks) {
      if (ch.kind === "max") {
        if (max === null || ch.value < max)
          max = ch.value;
      }
    }
    return max;
  }
};
ZodBigInt.create = (params) => {
  return new ZodBigInt({
    checks: [],
    typeName: ZodFirstPartyTypeKind.ZodBigInt,
    coerce: params?.coerce ?? false,
    ...processCreateParams(params)
  });
};
var ZodBoolean = class extends ZodType {
  _parse(input) {
    if (this._def.coerce) {
      input.data = Boolean(input.data);
    }
    const parsedType = this._getType(input);
    if (parsedType !== ZodParsedType.boolean) {
      const ctx = this._getOrReturnCtx(input);
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.boolean,
        received: ctx.parsedType
      });
      return INVALID;
    }
    return OK(input.data);
  }
};
ZodBoolean.create = (params) => {
  return new ZodBoolean({
    typeName: ZodFirstPartyTypeKind.ZodBoolean,
    coerce: params?.coerce || false,
    ...processCreateParams(params)
  });
};
var ZodDate = class _ZodDate extends ZodType {
  _parse(input) {
    if (this._def.coerce) {
      input.data = new Date(input.data);
    }
    const parsedType = this._getType(input);
    if (parsedType !== ZodParsedType.date) {
      const ctx2 = this._getOrReturnCtx(input);
      addIssueToContext(ctx2, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.date,
        received: ctx2.parsedType
      });
      return INVALID;
    }
    if (Number.isNaN(input.data.getTime())) {
      const ctx2 = this._getOrReturnCtx(input);
      addIssueToContext(ctx2, {
        code: ZodIssueCode.invalid_date
      });
      return INVALID;
    }
    const status = new ParseStatus();
    let ctx = void 0;
    for (const check of this._def.checks) {
      if (check.kind === "min") {
        if (input.data.getTime() < check.value) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.too_small,
            message: check.message,
            inclusive: true,
            exact: false,
            minimum: check.value,
            type: "date"
          });
          status.dirty();
        }
      } else if (check.kind === "max") {
        if (input.data.getTime() > check.value) {
          ctx = this._getOrReturnCtx(input, ctx);
          addIssueToContext(ctx, {
            code: ZodIssueCode.too_big,
            message: check.message,
            inclusive: true,
            exact: false,
            maximum: check.value,
            type: "date"
          });
          status.dirty();
        }
      } else {
        util.assertNever(check);
      }
    }
    return {
      status: status.value,
      value: new Date(input.data.getTime())
    };
  }
  _addCheck(check) {
    return new _ZodDate({
      ...this._def,
      checks: [...this._def.checks, check]
    });
  }
  min(minDate, message) {
    return this._addCheck({
      kind: "min",
      value: minDate.getTime(),
      message: errorUtil.toString(message)
    });
  }
  max(maxDate, message) {
    return this._addCheck({
      kind: "max",
      value: maxDate.getTime(),
      message: errorUtil.toString(message)
    });
  }
  get minDate() {
    let min = null;
    for (const ch of this._def.checks) {
      if (ch.kind === "min") {
        if (min === null || ch.value > min)
          min = ch.value;
      }
    }
    return min != null ? new Date(min) : null;
  }
  get maxDate() {
    let max = null;
    for (const ch of this._def.checks) {
      if (ch.kind === "max") {
        if (max === null || ch.value < max)
          max = ch.value;
      }
    }
    return max != null ? new Date(max) : null;
  }
};
ZodDate.create = (params) => {
  return new ZodDate({
    checks: [],
    coerce: params?.coerce || false,
    typeName: ZodFirstPartyTypeKind.ZodDate,
    ...processCreateParams(params)
  });
};
var ZodSymbol = class extends ZodType {
  _parse(input) {
    const parsedType = this._getType(input);
    if (parsedType !== ZodParsedType.symbol) {
      const ctx = this._getOrReturnCtx(input);
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.symbol,
        received: ctx.parsedType
      });
      return INVALID;
    }
    return OK(input.data);
  }
};
ZodSymbol.create = (params) => {
  return new ZodSymbol({
    typeName: ZodFirstPartyTypeKind.ZodSymbol,
    ...processCreateParams(params)
  });
};
var ZodUndefined = class extends ZodType {
  _parse(input) {
    const parsedType = this._getType(input);
    if (parsedType !== ZodParsedType.undefined) {
      const ctx = this._getOrReturnCtx(input);
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.undefined,
        received: ctx.parsedType
      });
      return INVALID;
    }
    return OK(input.data);
  }
};
ZodUndefined.create = (params) => {
  return new ZodUndefined({
    typeName: ZodFirstPartyTypeKind.ZodUndefined,
    ...processCreateParams(params)
  });
};
var ZodNull = class extends ZodType {
  _parse(input) {
    const parsedType = this._getType(input);
    if (parsedType !== ZodParsedType.null) {
      const ctx = this._getOrReturnCtx(input);
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.null,
        received: ctx.parsedType
      });
      return INVALID;
    }
    return OK(input.data);
  }
};
ZodNull.create = (params) => {
  return new ZodNull({
    typeName: ZodFirstPartyTypeKind.ZodNull,
    ...processCreateParams(params)
  });
};
var ZodAny = class extends ZodType {
  constructor() {
    super(...arguments);
    this._any = true;
  }
  _parse(input) {
    return OK(input.data);
  }
};
ZodAny.create = (params) => {
  return new ZodAny({
    typeName: ZodFirstPartyTypeKind.ZodAny,
    ...processCreateParams(params)
  });
};
var ZodUnknown = class extends ZodType {
  constructor() {
    super(...arguments);
    this._unknown = true;
  }
  _parse(input) {
    return OK(input.data);
  }
};
ZodUnknown.create = (params) => {
  return new ZodUnknown({
    typeName: ZodFirstPartyTypeKind.ZodUnknown,
    ...processCreateParams(params)
  });
};
var ZodNever = class extends ZodType {
  _parse(input) {
    const ctx = this._getOrReturnCtx(input);
    addIssueToContext(ctx, {
      code: ZodIssueCode.invalid_type,
      expected: ZodParsedType.never,
      received: ctx.parsedType
    });
    return INVALID;
  }
};
ZodNever.create = (params) => {
  return new ZodNever({
    typeName: ZodFirstPartyTypeKind.ZodNever,
    ...processCreateParams(params)
  });
};
var ZodVoid = class extends ZodType {
  _parse(input) {
    const parsedType = this._getType(input);
    if (parsedType !== ZodParsedType.undefined) {
      const ctx = this._getOrReturnCtx(input);
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.void,
        received: ctx.parsedType
      });
      return INVALID;
    }
    return OK(input.data);
  }
};
ZodVoid.create = (params) => {
  return new ZodVoid({
    typeName: ZodFirstPartyTypeKind.ZodVoid,
    ...processCreateParams(params)
  });
};
var ZodArray = class _ZodArray extends ZodType {
  _parse(input) {
    const { ctx, status } = this._processInputParams(input);
    const def = this._def;
    if (ctx.parsedType !== ZodParsedType.array) {
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.array,
        received: ctx.parsedType
      });
      return INVALID;
    }
    if (def.exactLength !== null) {
      const tooBig = ctx.data.length > def.exactLength.value;
      const tooSmall = ctx.data.length < def.exactLength.value;
      if (tooBig || tooSmall) {
        addIssueToContext(ctx, {
          code: tooBig ? ZodIssueCode.too_big : ZodIssueCode.too_small,
          minimum: tooSmall ? def.exactLength.value : void 0,
          maximum: tooBig ? def.exactLength.value : void 0,
          type: "array",
          inclusive: true,
          exact: true,
          message: def.exactLength.message
        });
        status.dirty();
      }
    }
    if (def.minLength !== null) {
      if (ctx.data.length < def.minLength.value) {
        addIssueToContext(ctx, {
          code: ZodIssueCode.too_small,
          minimum: def.minLength.value,
          type: "array",
          inclusive: true,
          exact: false,
          message: def.minLength.message
        });
        status.dirty();
      }
    }
    if (def.maxLength !== null) {
      if (ctx.data.length > def.maxLength.value) {
        addIssueToContext(ctx, {
          code: ZodIssueCode.too_big,
          maximum: def.maxLength.value,
          type: "array",
          inclusive: true,
          exact: false,
          message: def.maxLength.message
        });
        status.dirty();
      }
    }
    if (ctx.common.async) {
      return Promise.all([...ctx.data].map((item, i) => {
        return def.type._parseAsync(new ParseInputLazyPath(ctx, item, ctx.path, i));
      })).then((result2) => {
        return ParseStatus.mergeArray(status, result2);
      });
    }
    const result = [...ctx.data].map((item, i) => {
      return def.type._parseSync(new ParseInputLazyPath(ctx, item, ctx.path, i));
    });
    return ParseStatus.mergeArray(status, result);
  }
  get element() {
    return this._def.type;
  }
  min(minLength, message) {
    return new _ZodArray({
      ...this._def,
      minLength: { value: minLength, message: errorUtil.toString(message) }
    });
  }
  max(maxLength, message) {
    return new _ZodArray({
      ...this._def,
      maxLength: { value: maxLength, message: errorUtil.toString(message) }
    });
  }
  length(len, message) {
    return new _ZodArray({
      ...this._def,
      exactLength: { value: len, message: errorUtil.toString(message) }
    });
  }
  nonempty(message) {
    return this.min(1, message);
  }
};
ZodArray.create = (schema, params) => {
  return new ZodArray({
    type: schema,
    minLength: null,
    maxLength: null,
    exactLength: null,
    typeName: ZodFirstPartyTypeKind.ZodArray,
    ...processCreateParams(params)
  });
};
function deepPartialify(schema) {
  if (schema instanceof ZodObject) {
    const newShape = {};
    for (const key in schema.shape) {
      const fieldSchema = schema.shape[key];
      newShape[key] = ZodOptional.create(deepPartialify(fieldSchema));
    }
    return new ZodObject({
      ...schema._def,
      shape: () => newShape
    });
  } else if (schema instanceof ZodArray) {
    return new ZodArray({
      ...schema._def,
      type: deepPartialify(schema.element)
    });
  } else if (schema instanceof ZodOptional) {
    return ZodOptional.create(deepPartialify(schema.unwrap()));
  } else if (schema instanceof ZodNullable) {
    return ZodNullable.create(deepPartialify(schema.unwrap()));
  } else if (schema instanceof ZodTuple) {
    return ZodTuple.create(schema.items.map((item) => deepPartialify(item)));
  } else {
    return schema;
  }
}
var ZodObject = class _ZodObject extends ZodType {
  constructor() {
    super(...arguments);
    this._cached = null;
    this.nonstrict = this.passthrough;
    this.augment = this.extend;
  }
  _getCached() {
    if (this._cached !== null)
      return this._cached;
    const shape2 = this._def.shape();
    const keys = util.objectKeys(shape2);
    this._cached = { shape: shape2, keys };
    return this._cached;
  }
  _parse(input) {
    const parsedType = this._getType(input);
    if (parsedType !== ZodParsedType.object) {
      const ctx2 = this._getOrReturnCtx(input);
      addIssueToContext(ctx2, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.object,
        received: ctx2.parsedType
      });
      return INVALID;
    }
    const { status, ctx } = this._processInputParams(input);
    const { shape: shape2, keys: shapeKeys } = this._getCached();
    const extraKeys = [];
    if (!(this._def.catchall instanceof ZodNever && this._def.unknownKeys === "strip")) {
      for (const key in ctx.data) {
        if (!shapeKeys.includes(key)) {
          extraKeys.push(key);
        }
      }
    }
    const pairs = [];
    for (const key of shapeKeys) {
      const keyValidator = shape2[key];
      const value = ctx.data[key];
      pairs.push({
        key: { status: "valid", value: key },
        value: keyValidator._parse(new ParseInputLazyPath(ctx, value, ctx.path, key)),
        alwaysSet: key in ctx.data
      });
    }
    if (this._def.catchall instanceof ZodNever) {
      const unknownKeys = this._def.unknownKeys;
      if (unknownKeys === "passthrough") {
        for (const key of extraKeys) {
          pairs.push({
            key: { status: "valid", value: key },
            value: { status: "valid", value: ctx.data[key] }
          });
        }
      } else if (unknownKeys === "strict") {
        if (extraKeys.length > 0) {
          addIssueToContext(ctx, {
            code: ZodIssueCode.unrecognized_keys,
            keys: extraKeys
          });
          status.dirty();
        }
      } else if (unknownKeys === "strip") {
      } else {
        throw new Error(`Internal ZodObject error: invalid unknownKeys value.`);
      }
    } else {
      const catchall = this._def.catchall;
      for (const key of extraKeys) {
        const value = ctx.data[key];
        pairs.push({
          key: { status: "valid", value: key },
          value: catchall._parse(
            new ParseInputLazyPath(ctx, value, ctx.path, key)
            //, ctx.child(key), value, getParsedType(value)
          ),
          alwaysSet: key in ctx.data
        });
      }
    }
    if (ctx.common.async) {
      return Promise.resolve().then(async () => {
        const syncPairs = [];
        for (const pair of pairs) {
          const key = await pair.key;
          const value = await pair.value;
          syncPairs.push({
            key,
            value,
            alwaysSet: pair.alwaysSet
          });
        }
        return syncPairs;
      }).then((syncPairs) => {
        return ParseStatus.mergeObjectSync(status, syncPairs);
      });
    } else {
      return ParseStatus.mergeObjectSync(status, pairs);
    }
  }
  get shape() {
    return this._def.shape();
  }
  strict(message) {
    errorUtil.errToObj;
    return new _ZodObject({
      ...this._def,
      unknownKeys: "strict",
      ...message !== void 0 ? {
        errorMap: (issue, ctx) => {
          const defaultError = this._def.errorMap?.(issue, ctx).message ?? ctx.defaultError;
          if (issue.code === "unrecognized_keys")
            return {
              message: errorUtil.errToObj(message).message ?? defaultError
            };
          return {
            message: defaultError
          };
        }
      } : {}
    });
  }
  strip() {
    return new _ZodObject({
      ...this._def,
      unknownKeys: "strip"
    });
  }
  passthrough() {
    return new _ZodObject({
      ...this._def,
      unknownKeys: "passthrough"
    });
  }
  // const AugmentFactory =
  //   <Def extends ZodObjectDef>(def: Def) =>
  //   <Augmentation extends ZodRawShape>(
  //     augmentation: Augmentation
  //   ): ZodObject<
  //     extendShape<ReturnType<Def["shape"]>, Augmentation>,
  //     Def["unknownKeys"],
  //     Def["catchall"]
  //   > => {
  //     return new ZodObject({
  //       ...def,
  //       shape: () => ({
  //         ...def.shape(),
  //         ...augmentation,
  //       }),
  //     }) as any;
  //   };
  extend(augmentation) {
    return new _ZodObject({
      ...this._def,
      shape: () => ({
        ...this._def.shape(),
        ...augmentation
      })
    });
  }
  /**
   * Prior to zod@1.0.12 there was a bug in the
   * inferred type of merged objects. Please
   * upgrade if you are experiencing issues.
   */
  merge(merging) {
    const merged = new _ZodObject({
      unknownKeys: merging._def.unknownKeys,
      catchall: merging._def.catchall,
      shape: () => ({
        ...this._def.shape(),
        ...merging._def.shape()
      }),
      typeName: ZodFirstPartyTypeKind.ZodObject
    });
    return merged;
  }
  // merge<
  //   Incoming extends AnyZodObject,
  //   Augmentation extends Incoming["shape"],
  //   NewOutput extends {
  //     [k in keyof Augmentation | keyof Output]: k extends keyof Augmentation
  //       ? Augmentation[k]["_output"]
  //       : k extends keyof Output
  //       ? Output[k]
  //       : never;
  //   },
  //   NewInput extends {
  //     [k in keyof Augmentation | keyof Input]: k extends keyof Augmentation
  //       ? Augmentation[k]["_input"]
  //       : k extends keyof Input
  //       ? Input[k]
  //       : never;
  //   }
  // >(
  //   merging: Incoming
  // ): ZodObject<
  //   extendShape<T, ReturnType<Incoming["_def"]["shape"]>>,
  //   Incoming["_def"]["unknownKeys"],
  //   Incoming["_def"]["catchall"],
  //   NewOutput,
  //   NewInput
  // > {
  //   const merged: any = new ZodObject({
  //     unknownKeys: merging._def.unknownKeys,
  //     catchall: merging._def.catchall,
  //     shape: () =>
  //       objectUtil.mergeShapes(this._def.shape(), merging._def.shape()),
  //     typeName: ZodFirstPartyTypeKind.ZodObject,
  //   }) as any;
  //   return merged;
  // }
  setKey(key, schema) {
    return this.augment({ [key]: schema });
  }
  // merge<Incoming extends AnyZodObject>(
  //   merging: Incoming
  // ): //ZodObject<T & Incoming["_shape"], UnknownKeys, Catchall> = (merging) => {
  // ZodObject<
  //   extendShape<T, ReturnType<Incoming["_def"]["shape"]>>,
  //   Incoming["_def"]["unknownKeys"],
  //   Incoming["_def"]["catchall"]
  // > {
  //   // const mergedShape = objectUtil.mergeShapes(
  //   //   this._def.shape(),
  //   //   merging._def.shape()
  //   // );
  //   const merged: any = new ZodObject({
  //     unknownKeys: merging._def.unknownKeys,
  //     catchall: merging._def.catchall,
  //     shape: () =>
  //       objectUtil.mergeShapes(this._def.shape(), merging._def.shape()),
  //     typeName: ZodFirstPartyTypeKind.ZodObject,
  //   }) as any;
  //   return merged;
  // }
  catchall(index) {
    return new _ZodObject({
      ...this._def,
      catchall: index
    });
  }
  pick(mask) {
    const shape2 = {};
    for (const key of util.objectKeys(mask)) {
      if (mask[key] && this.shape[key]) {
        shape2[key] = this.shape[key];
      }
    }
    return new _ZodObject({
      ...this._def,
      shape: () => shape2
    });
  }
  omit(mask) {
    const shape2 = {};
    for (const key of util.objectKeys(this.shape)) {
      if (!mask[key]) {
        shape2[key] = this.shape[key];
      }
    }
    return new _ZodObject({
      ...this._def,
      shape: () => shape2
    });
  }
  /**
   * @deprecated
   */
  deepPartial() {
    return deepPartialify(this);
  }
  partial(mask) {
    const newShape = {};
    for (const key of util.objectKeys(this.shape)) {
      const fieldSchema = this.shape[key];
      if (mask && !mask[key]) {
        newShape[key] = fieldSchema;
      } else {
        newShape[key] = fieldSchema.optional();
      }
    }
    return new _ZodObject({
      ...this._def,
      shape: () => newShape
    });
  }
  required(mask) {
    const newShape = {};
    for (const key of util.objectKeys(this.shape)) {
      if (mask && !mask[key]) {
        newShape[key] = this.shape[key];
      } else {
        const fieldSchema = this.shape[key];
        let newField = fieldSchema;
        while (newField instanceof ZodOptional) {
          newField = newField._def.innerType;
        }
        newShape[key] = newField;
      }
    }
    return new _ZodObject({
      ...this._def,
      shape: () => newShape
    });
  }
  keyof() {
    return createZodEnum(util.objectKeys(this.shape));
  }
};
ZodObject.create = (shape2, params) => {
  return new ZodObject({
    shape: () => shape2,
    unknownKeys: "strip",
    catchall: ZodNever.create(),
    typeName: ZodFirstPartyTypeKind.ZodObject,
    ...processCreateParams(params)
  });
};
ZodObject.strictCreate = (shape2, params) => {
  return new ZodObject({
    shape: () => shape2,
    unknownKeys: "strict",
    catchall: ZodNever.create(),
    typeName: ZodFirstPartyTypeKind.ZodObject,
    ...processCreateParams(params)
  });
};
ZodObject.lazycreate = (shape2, params) => {
  return new ZodObject({
    shape: shape2,
    unknownKeys: "strip",
    catchall: ZodNever.create(),
    typeName: ZodFirstPartyTypeKind.ZodObject,
    ...processCreateParams(params)
  });
};
var ZodUnion = class extends ZodType {
  _parse(input) {
    const { ctx } = this._processInputParams(input);
    const options = this._def.options;
    function handleResults(results) {
      for (const result of results) {
        if (result.result.status === "valid") {
          return result.result;
        }
      }
      for (const result of results) {
        if (result.result.status === "dirty") {
          ctx.common.issues.push(...result.ctx.common.issues);
          return result.result;
        }
      }
      const unionErrors = results.map((result) => new ZodError(result.ctx.common.issues));
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_union,
        unionErrors
      });
      return INVALID;
    }
    if (ctx.common.async) {
      return Promise.all(options.map(async (option) => {
        const childCtx = {
          ...ctx,
          common: {
            ...ctx.common,
            issues: []
          },
          parent: null
        };
        return {
          result: await option._parseAsync({
            data: ctx.data,
            path: ctx.path,
            parent: childCtx
          }),
          ctx: childCtx
        };
      })).then(handleResults);
    } else {
      let dirty = void 0;
      const issues = [];
      for (const option of options) {
        const childCtx = {
          ...ctx,
          common: {
            ...ctx.common,
            issues: []
          },
          parent: null
        };
        const result = option._parseSync({
          data: ctx.data,
          path: ctx.path,
          parent: childCtx
        });
        if (result.status === "valid") {
          return result;
        } else if (result.status === "dirty" && !dirty) {
          dirty = { result, ctx: childCtx };
        }
        if (childCtx.common.issues.length) {
          issues.push(childCtx.common.issues);
        }
      }
      if (dirty) {
        ctx.common.issues.push(...dirty.ctx.common.issues);
        return dirty.result;
      }
      const unionErrors = issues.map((issues2) => new ZodError(issues2));
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_union,
        unionErrors
      });
      return INVALID;
    }
  }
  get options() {
    return this._def.options;
  }
};
ZodUnion.create = (types, params) => {
  return new ZodUnion({
    options: types,
    typeName: ZodFirstPartyTypeKind.ZodUnion,
    ...processCreateParams(params)
  });
};
var getDiscriminator = (type) => {
  if (type instanceof ZodLazy) {
    return getDiscriminator(type.schema);
  } else if (type instanceof ZodEffects) {
    return getDiscriminator(type.innerType());
  } else if (type instanceof ZodLiteral) {
    return [type.value];
  } else if (type instanceof ZodEnum) {
    return type.options;
  } else if (type instanceof ZodNativeEnum) {
    return util.objectValues(type.enum);
  } else if (type instanceof ZodDefault) {
    return getDiscriminator(type._def.innerType);
  } else if (type instanceof ZodUndefined) {
    return [void 0];
  } else if (type instanceof ZodNull) {
    return [null];
  } else if (type instanceof ZodOptional) {
    return [void 0, ...getDiscriminator(type.unwrap())];
  } else if (type instanceof ZodNullable) {
    return [null, ...getDiscriminator(type.unwrap())];
  } else if (type instanceof ZodBranded) {
    return getDiscriminator(type.unwrap());
  } else if (type instanceof ZodReadonly) {
    return getDiscriminator(type.unwrap());
  } else if (type instanceof ZodCatch) {
    return getDiscriminator(type._def.innerType);
  } else {
    return [];
  }
};
var ZodDiscriminatedUnion = class _ZodDiscriminatedUnion extends ZodType {
  _parse(input) {
    const { ctx } = this._processInputParams(input);
    if (ctx.parsedType !== ZodParsedType.object) {
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.object,
        received: ctx.parsedType
      });
      return INVALID;
    }
    const discriminator = this.discriminator;
    const discriminatorValue = ctx.data[discriminator];
    const option = this.optionsMap.get(discriminatorValue);
    if (!option) {
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_union_discriminator,
        options: Array.from(this.optionsMap.keys()),
        path: [discriminator]
      });
      return INVALID;
    }
    if (ctx.common.async) {
      return option._parseAsync({
        data: ctx.data,
        path: ctx.path,
        parent: ctx
      });
    } else {
      return option._parseSync({
        data: ctx.data,
        path: ctx.path,
        parent: ctx
      });
    }
  }
  get discriminator() {
    return this._def.discriminator;
  }
  get options() {
    return this._def.options;
  }
  get optionsMap() {
    return this._def.optionsMap;
  }
  /**
   * The constructor of the discriminated union schema. Its behaviour is very similar to that of the normal z.union() constructor.
   * However, it only allows a union of objects, all of which need to share a discriminator property. This property must
   * have a different value for each object in the union.
   * @param discriminator the name of the discriminator property
   * @param types an array of object schemas
   * @param params
   */
  static create(discriminator, options, params) {
    const optionsMap = /* @__PURE__ */ new Map();
    for (const type of options) {
      const discriminatorValues = getDiscriminator(type.shape[discriminator]);
      if (!discriminatorValues.length) {
        throw new Error(`A discriminator value for key \`${discriminator}\` could not be extracted from all schema options`);
      }
      for (const value of discriminatorValues) {
        if (optionsMap.has(value)) {
          throw new Error(`Discriminator property ${String(discriminator)} has duplicate value ${String(value)}`);
        }
        optionsMap.set(value, type);
      }
    }
    return new _ZodDiscriminatedUnion({
      typeName: ZodFirstPartyTypeKind.ZodDiscriminatedUnion,
      discriminator,
      options,
      optionsMap,
      ...processCreateParams(params)
    });
  }
};
function mergeValues(a, b) {
  const aType = getParsedType(a);
  const bType = getParsedType(b);
  if (a === b) {
    return { valid: true, data: a };
  } else if (aType === ZodParsedType.object && bType === ZodParsedType.object) {
    const bKeys = util.objectKeys(b);
    const sharedKeys = util.objectKeys(a).filter((key) => bKeys.indexOf(key) !== -1);
    const newObj = { ...a, ...b };
    for (const key of sharedKeys) {
      const sharedValue = mergeValues(a[key], b[key]);
      if (!sharedValue.valid) {
        return { valid: false };
      }
      newObj[key] = sharedValue.data;
    }
    return { valid: true, data: newObj };
  } else if (aType === ZodParsedType.array && bType === ZodParsedType.array) {
    if (a.length !== b.length) {
      return { valid: false };
    }
    const newArray = [];
    for (let index = 0; index < a.length; index++) {
      const itemA = a[index];
      const itemB = b[index];
      const sharedValue = mergeValues(itemA, itemB);
      if (!sharedValue.valid) {
        return { valid: false };
      }
      newArray.push(sharedValue.data);
    }
    return { valid: true, data: newArray };
  } else if (aType === ZodParsedType.date && bType === ZodParsedType.date && +a === +b) {
    return { valid: true, data: a };
  } else {
    return { valid: false };
  }
}
var ZodIntersection = class extends ZodType {
  _parse(input) {
    const { status, ctx } = this._processInputParams(input);
    const handleParsed = (parsedLeft, parsedRight) => {
      if (isAborted(parsedLeft) || isAborted(parsedRight)) {
        return INVALID;
      }
      const merged = mergeValues(parsedLeft.value, parsedRight.value);
      if (!merged.valid) {
        addIssueToContext(ctx, {
          code: ZodIssueCode.invalid_intersection_types
        });
        return INVALID;
      }
      if (isDirty(parsedLeft) || isDirty(parsedRight)) {
        status.dirty();
      }
      return { status: status.value, value: merged.data };
    };
    if (ctx.common.async) {
      return Promise.all([
        this._def.left._parseAsync({
          data: ctx.data,
          path: ctx.path,
          parent: ctx
        }),
        this._def.right._parseAsync({
          data: ctx.data,
          path: ctx.path,
          parent: ctx
        })
      ]).then(([left, right]) => handleParsed(left, right));
    } else {
      return handleParsed(this._def.left._parseSync({
        data: ctx.data,
        path: ctx.path,
        parent: ctx
      }), this._def.right._parseSync({
        data: ctx.data,
        path: ctx.path,
        parent: ctx
      }));
    }
  }
};
ZodIntersection.create = (left, right, params) => {
  return new ZodIntersection({
    left,
    right,
    typeName: ZodFirstPartyTypeKind.ZodIntersection,
    ...processCreateParams(params)
  });
};
var ZodTuple = class _ZodTuple extends ZodType {
  _parse(input) {
    const { status, ctx } = this._processInputParams(input);
    if (ctx.parsedType !== ZodParsedType.array) {
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.array,
        received: ctx.parsedType
      });
      return INVALID;
    }
    if (ctx.data.length < this._def.items.length) {
      addIssueToContext(ctx, {
        code: ZodIssueCode.too_small,
        minimum: this._def.items.length,
        inclusive: true,
        exact: false,
        type: "array"
      });
      return INVALID;
    }
    const rest = this._def.rest;
    if (!rest && ctx.data.length > this._def.items.length) {
      addIssueToContext(ctx, {
        code: ZodIssueCode.too_big,
        maximum: this._def.items.length,
        inclusive: true,
        exact: false,
        type: "array"
      });
      status.dirty();
    }
    const items = [...ctx.data].map((item, itemIndex) => {
      const schema = this._def.items[itemIndex] || this._def.rest;
      if (!schema)
        return null;
      return schema._parse(new ParseInputLazyPath(ctx, item, ctx.path, itemIndex));
    }).filter((x) => !!x);
    if (ctx.common.async) {
      return Promise.all(items).then((results) => {
        return ParseStatus.mergeArray(status, results);
      });
    } else {
      return ParseStatus.mergeArray(status, items);
    }
  }
  get items() {
    return this._def.items;
  }
  rest(rest) {
    return new _ZodTuple({
      ...this._def,
      rest
    });
  }
};
ZodTuple.create = (schemas, params) => {
  if (!Array.isArray(schemas)) {
    throw new Error("You must pass an array of schemas to z.tuple([ ... ])");
  }
  return new ZodTuple({
    items: schemas,
    typeName: ZodFirstPartyTypeKind.ZodTuple,
    rest: null,
    ...processCreateParams(params)
  });
};
var ZodRecord = class _ZodRecord extends ZodType {
  get keySchema() {
    return this._def.keyType;
  }
  get valueSchema() {
    return this._def.valueType;
  }
  _parse(input) {
    const { status, ctx } = this._processInputParams(input);
    if (ctx.parsedType !== ZodParsedType.object) {
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.object,
        received: ctx.parsedType
      });
      return INVALID;
    }
    const pairs = [];
    const keyType = this._def.keyType;
    const valueType = this._def.valueType;
    for (const key in ctx.data) {
      pairs.push({
        key: keyType._parse(new ParseInputLazyPath(ctx, key, ctx.path, key)),
        value: valueType._parse(new ParseInputLazyPath(ctx, ctx.data[key], ctx.path, key)),
        alwaysSet: key in ctx.data
      });
    }
    if (ctx.common.async) {
      return ParseStatus.mergeObjectAsync(status, pairs);
    } else {
      return ParseStatus.mergeObjectSync(status, pairs);
    }
  }
  get element() {
    return this._def.valueType;
  }
  static create(first, second, third) {
    if (second instanceof ZodType) {
      return new _ZodRecord({
        keyType: first,
        valueType: second,
        typeName: ZodFirstPartyTypeKind.ZodRecord,
        ...processCreateParams(third)
      });
    }
    return new _ZodRecord({
      keyType: ZodString.create(),
      valueType: first,
      typeName: ZodFirstPartyTypeKind.ZodRecord,
      ...processCreateParams(second)
    });
  }
};
var ZodMap = class extends ZodType {
  get keySchema() {
    return this._def.keyType;
  }
  get valueSchema() {
    return this._def.valueType;
  }
  _parse(input) {
    const { status, ctx } = this._processInputParams(input);
    if (ctx.parsedType !== ZodParsedType.map) {
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.map,
        received: ctx.parsedType
      });
      return INVALID;
    }
    const keyType = this._def.keyType;
    const valueType = this._def.valueType;
    const pairs = [...ctx.data.entries()].map(([key, value], index) => {
      return {
        key: keyType._parse(new ParseInputLazyPath(ctx, key, ctx.path, [index, "key"])),
        value: valueType._parse(new ParseInputLazyPath(ctx, value, ctx.path, [index, "value"]))
      };
    });
    if (ctx.common.async) {
      const finalMap = /* @__PURE__ */ new Map();
      return Promise.resolve().then(async () => {
        for (const pair of pairs) {
          const key = await pair.key;
          const value = await pair.value;
          if (key.status === "aborted" || value.status === "aborted") {
            return INVALID;
          }
          if (key.status === "dirty" || value.status === "dirty") {
            status.dirty();
          }
          finalMap.set(key.value, value.value);
        }
        return { status: status.value, value: finalMap };
      });
    } else {
      const finalMap = /* @__PURE__ */ new Map();
      for (const pair of pairs) {
        const key = pair.key;
        const value = pair.value;
        if (key.status === "aborted" || value.status === "aborted") {
          return INVALID;
        }
        if (key.status === "dirty" || value.status === "dirty") {
          status.dirty();
        }
        finalMap.set(key.value, value.value);
      }
      return { status: status.value, value: finalMap };
    }
  }
};
ZodMap.create = (keyType, valueType, params) => {
  return new ZodMap({
    valueType,
    keyType,
    typeName: ZodFirstPartyTypeKind.ZodMap,
    ...processCreateParams(params)
  });
};
var ZodSet = class _ZodSet extends ZodType {
  _parse(input) {
    const { status, ctx } = this._processInputParams(input);
    if (ctx.parsedType !== ZodParsedType.set) {
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.set,
        received: ctx.parsedType
      });
      return INVALID;
    }
    const def = this._def;
    if (def.minSize !== null) {
      if (ctx.data.size < def.minSize.value) {
        addIssueToContext(ctx, {
          code: ZodIssueCode.too_small,
          minimum: def.minSize.value,
          type: "set",
          inclusive: true,
          exact: false,
          message: def.minSize.message
        });
        status.dirty();
      }
    }
    if (def.maxSize !== null) {
      if (ctx.data.size > def.maxSize.value) {
        addIssueToContext(ctx, {
          code: ZodIssueCode.too_big,
          maximum: def.maxSize.value,
          type: "set",
          inclusive: true,
          exact: false,
          message: def.maxSize.message
        });
        status.dirty();
      }
    }
    const valueType = this._def.valueType;
    function finalizeSet(elements2) {
      const parsedSet = /* @__PURE__ */ new Set();
      for (const element of elements2) {
        if (element.status === "aborted")
          return INVALID;
        if (element.status === "dirty")
          status.dirty();
        parsedSet.add(element.value);
      }
      return { status: status.value, value: parsedSet };
    }
    const elements = [...ctx.data.values()].map((item, i) => valueType._parse(new ParseInputLazyPath(ctx, item, ctx.path, i)));
    if (ctx.common.async) {
      return Promise.all(elements).then((elements2) => finalizeSet(elements2));
    } else {
      return finalizeSet(elements);
    }
  }
  min(minSize, message) {
    return new _ZodSet({
      ...this._def,
      minSize: { value: minSize, message: errorUtil.toString(message) }
    });
  }
  max(maxSize, message) {
    return new _ZodSet({
      ...this._def,
      maxSize: { value: maxSize, message: errorUtil.toString(message) }
    });
  }
  size(size, message) {
    return this.min(size, message).max(size, message);
  }
  nonempty(message) {
    return this.min(1, message);
  }
};
ZodSet.create = (valueType, params) => {
  return new ZodSet({
    valueType,
    minSize: null,
    maxSize: null,
    typeName: ZodFirstPartyTypeKind.ZodSet,
    ...processCreateParams(params)
  });
};
var ZodFunction = class _ZodFunction extends ZodType {
  constructor() {
    super(...arguments);
    this.validate = this.implement;
  }
  _parse(input) {
    const { ctx } = this._processInputParams(input);
    if (ctx.parsedType !== ZodParsedType.function) {
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.function,
        received: ctx.parsedType
      });
      return INVALID;
    }
    function makeArgsIssue(args, error) {
      return makeIssue({
        data: args,
        path: ctx.path,
        errorMaps: [ctx.common.contextualErrorMap, ctx.schemaErrorMap, getErrorMap(), en_default].filter((x) => !!x),
        issueData: {
          code: ZodIssueCode.invalid_arguments,
          argumentsError: error
        }
      });
    }
    function makeReturnsIssue(returns, error) {
      return makeIssue({
        data: returns,
        path: ctx.path,
        errorMaps: [ctx.common.contextualErrorMap, ctx.schemaErrorMap, getErrorMap(), en_default].filter((x) => !!x),
        issueData: {
          code: ZodIssueCode.invalid_return_type,
          returnTypeError: error
        }
      });
    }
    const params = { errorMap: ctx.common.contextualErrorMap };
    const fn = ctx.data;
    if (this._def.returns instanceof ZodPromise) {
      const me = this;
      return OK(async function(...args) {
        const error = new ZodError([]);
        const parsedArgs = await me._def.args.parseAsync(args, params).catch((e) => {
          error.addIssue(makeArgsIssue(args, e));
          throw error;
        });
        const result = await Reflect.apply(fn, this, parsedArgs);
        const parsedReturns = await me._def.returns._def.type.parseAsync(result, params).catch((e) => {
          error.addIssue(makeReturnsIssue(result, e));
          throw error;
        });
        return parsedReturns;
      });
    } else {
      const me = this;
      return OK(function(...args) {
        const parsedArgs = me._def.args.safeParse(args, params);
        if (!parsedArgs.success) {
          throw new ZodError([makeArgsIssue(args, parsedArgs.error)]);
        }
        const result = Reflect.apply(fn, this, parsedArgs.data);
        const parsedReturns = me._def.returns.safeParse(result, params);
        if (!parsedReturns.success) {
          throw new ZodError([makeReturnsIssue(result, parsedReturns.error)]);
        }
        return parsedReturns.data;
      });
    }
  }
  parameters() {
    return this._def.args;
  }
  returnType() {
    return this._def.returns;
  }
  args(...items) {
    return new _ZodFunction({
      ...this._def,
      args: ZodTuple.create(items).rest(ZodUnknown.create())
    });
  }
  returns(returnType) {
    return new _ZodFunction({
      ...this._def,
      returns: returnType
    });
  }
  implement(func) {
    const validatedFunc = this.parse(func);
    return validatedFunc;
  }
  strictImplement(func) {
    const validatedFunc = this.parse(func);
    return validatedFunc;
  }
  static create(args, returns, params) {
    return new _ZodFunction({
      args: args ? args : ZodTuple.create([]).rest(ZodUnknown.create()),
      returns: returns || ZodUnknown.create(),
      typeName: ZodFirstPartyTypeKind.ZodFunction,
      ...processCreateParams(params)
    });
  }
};
var ZodLazy = class extends ZodType {
  get schema() {
    return this._def.getter();
  }
  _parse(input) {
    const { ctx } = this._processInputParams(input);
    const lazySchema = this._def.getter();
    return lazySchema._parse({ data: ctx.data, path: ctx.path, parent: ctx });
  }
};
ZodLazy.create = (getter, params) => {
  return new ZodLazy({
    getter,
    typeName: ZodFirstPartyTypeKind.ZodLazy,
    ...processCreateParams(params)
  });
};
var ZodLiteral = class extends ZodType {
  _parse(input) {
    if (input.data !== this._def.value) {
      const ctx = this._getOrReturnCtx(input);
      addIssueToContext(ctx, {
        received: ctx.data,
        code: ZodIssueCode.invalid_literal,
        expected: this._def.value
      });
      return INVALID;
    }
    return { status: "valid", value: input.data };
  }
  get value() {
    return this._def.value;
  }
};
ZodLiteral.create = (value, params) => {
  return new ZodLiteral({
    value,
    typeName: ZodFirstPartyTypeKind.ZodLiteral,
    ...processCreateParams(params)
  });
};
function createZodEnum(values, params) {
  return new ZodEnum({
    values,
    typeName: ZodFirstPartyTypeKind.ZodEnum,
    ...processCreateParams(params)
  });
}
var ZodEnum = class _ZodEnum extends ZodType {
  _parse(input) {
    if (typeof input.data !== "string") {
      const ctx = this._getOrReturnCtx(input);
      const expectedValues = this._def.values;
      addIssueToContext(ctx, {
        expected: util.joinValues(expectedValues),
        received: ctx.parsedType,
        code: ZodIssueCode.invalid_type
      });
      return INVALID;
    }
    if (!this._cache) {
      this._cache = new Set(this._def.values);
    }
    if (!this._cache.has(input.data)) {
      const ctx = this._getOrReturnCtx(input);
      const expectedValues = this._def.values;
      addIssueToContext(ctx, {
        received: ctx.data,
        code: ZodIssueCode.invalid_enum_value,
        options: expectedValues
      });
      return INVALID;
    }
    return OK(input.data);
  }
  get options() {
    return this._def.values;
  }
  get enum() {
    const enumValues = {};
    for (const val of this._def.values) {
      enumValues[val] = val;
    }
    return enumValues;
  }
  get Values() {
    const enumValues = {};
    for (const val of this._def.values) {
      enumValues[val] = val;
    }
    return enumValues;
  }
  get Enum() {
    const enumValues = {};
    for (const val of this._def.values) {
      enumValues[val] = val;
    }
    return enumValues;
  }
  extract(values, newDef = this._def) {
    return _ZodEnum.create(values, {
      ...this._def,
      ...newDef
    });
  }
  exclude(values, newDef = this._def) {
    return _ZodEnum.create(this.options.filter((opt) => !values.includes(opt)), {
      ...this._def,
      ...newDef
    });
  }
};
ZodEnum.create = createZodEnum;
var ZodNativeEnum = class extends ZodType {
  _parse(input) {
    const nativeEnumValues = util.getValidEnumValues(this._def.values);
    const ctx = this._getOrReturnCtx(input);
    if (ctx.parsedType !== ZodParsedType.string && ctx.parsedType !== ZodParsedType.number) {
      const expectedValues = util.objectValues(nativeEnumValues);
      addIssueToContext(ctx, {
        expected: util.joinValues(expectedValues),
        received: ctx.parsedType,
        code: ZodIssueCode.invalid_type
      });
      return INVALID;
    }
    if (!this._cache) {
      this._cache = new Set(util.getValidEnumValues(this._def.values));
    }
    if (!this._cache.has(input.data)) {
      const expectedValues = util.objectValues(nativeEnumValues);
      addIssueToContext(ctx, {
        received: ctx.data,
        code: ZodIssueCode.invalid_enum_value,
        options: expectedValues
      });
      return INVALID;
    }
    return OK(input.data);
  }
  get enum() {
    return this._def.values;
  }
};
ZodNativeEnum.create = (values, params) => {
  return new ZodNativeEnum({
    values,
    typeName: ZodFirstPartyTypeKind.ZodNativeEnum,
    ...processCreateParams(params)
  });
};
var ZodPromise = class extends ZodType {
  unwrap() {
    return this._def.type;
  }
  _parse(input) {
    const { ctx } = this._processInputParams(input);
    if (ctx.parsedType !== ZodParsedType.promise && ctx.common.async === false) {
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.promise,
        received: ctx.parsedType
      });
      return INVALID;
    }
    const promisified = ctx.parsedType === ZodParsedType.promise ? ctx.data : Promise.resolve(ctx.data);
    return OK(promisified.then((data) => {
      return this._def.type.parseAsync(data, {
        path: ctx.path,
        errorMap: ctx.common.contextualErrorMap
      });
    }));
  }
};
ZodPromise.create = (schema, params) => {
  return new ZodPromise({
    type: schema,
    typeName: ZodFirstPartyTypeKind.ZodPromise,
    ...processCreateParams(params)
  });
};
var ZodEffects = class extends ZodType {
  innerType() {
    return this._def.schema;
  }
  sourceType() {
    return this._def.schema._def.typeName === ZodFirstPartyTypeKind.ZodEffects ? this._def.schema.sourceType() : this._def.schema;
  }
  _parse(input) {
    const { status, ctx } = this._processInputParams(input);
    const effect = this._def.effect || null;
    const checkCtx = {
      addIssue: (arg) => {
        addIssueToContext(ctx, arg);
        if (arg.fatal) {
          status.abort();
        } else {
          status.dirty();
        }
      },
      get path() {
        return ctx.path;
      }
    };
    checkCtx.addIssue = checkCtx.addIssue.bind(checkCtx);
    if (effect.type === "preprocess") {
      const processed = effect.transform(ctx.data, checkCtx);
      if (ctx.common.async) {
        return Promise.resolve(processed).then(async (processed2) => {
          if (status.value === "aborted")
            return INVALID;
          const result = await this._def.schema._parseAsync({
            data: processed2,
            path: ctx.path,
            parent: ctx
          });
          if (result.status === "aborted")
            return INVALID;
          if (result.status === "dirty")
            return DIRTY(result.value);
          if (status.value === "dirty")
            return DIRTY(result.value);
          return result;
        });
      } else {
        if (status.value === "aborted")
          return INVALID;
        const result = this._def.schema._parseSync({
          data: processed,
          path: ctx.path,
          parent: ctx
        });
        if (result.status === "aborted")
          return INVALID;
        if (result.status === "dirty")
          return DIRTY(result.value);
        if (status.value === "dirty")
          return DIRTY(result.value);
        return result;
      }
    }
    if (effect.type === "refinement") {
      const executeRefinement = (acc) => {
        const result = effect.refinement(acc, checkCtx);
        if (ctx.common.async) {
          return Promise.resolve(result);
        }
        if (result instanceof Promise) {
          throw new Error("Async refinement encountered during synchronous parse operation. Use .parseAsync instead.");
        }
        return acc;
      };
      if (ctx.common.async === false) {
        const inner = this._def.schema._parseSync({
          data: ctx.data,
          path: ctx.path,
          parent: ctx
        });
        if (inner.status === "aborted")
          return INVALID;
        if (inner.status === "dirty")
          status.dirty();
        executeRefinement(inner.value);
        return { status: status.value, value: inner.value };
      } else {
        return this._def.schema._parseAsync({ data: ctx.data, path: ctx.path, parent: ctx }).then((inner) => {
          if (inner.status === "aborted")
            return INVALID;
          if (inner.status === "dirty")
            status.dirty();
          return executeRefinement(inner.value).then(() => {
            return { status: status.value, value: inner.value };
          });
        });
      }
    }
    if (effect.type === "transform") {
      if (ctx.common.async === false) {
        const base3 = this._def.schema._parseSync({
          data: ctx.data,
          path: ctx.path,
          parent: ctx
        });
        if (!isValid(base3))
          return INVALID;
        const result = effect.transform(base3.value, checkCtx);
        if (result instanceof Promise) {
          throw new Error(`Asynchronous transform encountered during synchronous parse operation. Use .parseAsync instead.`);
        }
        return { status: status.value, value: result };
      } else {
        return this._def.schema._parseAsync({ data: ctx.data, path: ctx.path, parent: ctx }).then((base3) => {
          if (!isValid(base3))
            return INVALID;
          return Promise.resolve(effect.transform(base3.value, checkCtx)).then((result) => ({
            status: status.value,
            value: result
          }));
        });
      }
    }
    util.assertNever(effect);
  }
};
ZodEffects.create = (schema, effect, params) => {
  return new ZodEffects({
    schema,
    typeName: ZodFirstPartyTypeKind.ZodEffects,
    effect,
    ...processCreateParams(params)
  });
};
ZodEffects.createWithPreprocess = (preprocess, schema, params) => {
  return new ZodEffects({
    schema,
    effect: { type: "preprocess", transform: preprocess },
    typeName: ZodFirstPartyTypeKind.ZodEffects,
    ...processCreateParams(params)
  });
};
var ZodOptional = class extends ZodType {
  _parse(input) {
    const parsedType = this._getType(input);
    if (parsedType === ZodParsedType.undefined) {
      return OK(void 0);
    }
    return this._def.innerType._parse(input);
  }
  unwrap() {
    return this._def.innerType;
  }
};
ZodOptional.create = (type, params) => {
  return new ZodOptional({
    innerType: type,
    typeName: ZodFirstPartyTypeKind.ZodOptional,
    ...processCreateParams(params)
  });
};
var ZodNullable = class extends ZodType {
  _parse(input) {
    const parsedType = this._getType(input);
    if (parsedType === ZodParsedType.null) {
      return OK(null);
    }
    return this._def.innerType._parse(input);
  }
  unwrap() {
    return this._def.innerType;
  }
};
ZodNullable.create = (type, params) => {
  return new ZodNullable({
    innerType: type,
    typeName: ZodFirstPartyTypeKind.ZodNullable,
    ...processCreateParams(params)
  });
};
var ZodDefault = class extends ZodType {
  _parse(input) {
    const { ctx } = this._processInputParams(input);
    let data = ctx.data;
    if (ctx.parsedType === ZodParsedType.undefined) {
      data = this._def.defaultValue();
    }
    return this._def.innerType._parse({
      data,
      path: ctx.path,
      parent: ctx
    });
  }
  removeDefault() {
    return this._def.innerType;
  }
};
ZodDefault.create = (type, params) => {
  return new ZodDefault({
    innerType: type,
    typeName: ZodFirstPartyTypeKind.ZodDefault,
    defaultValue: typeof params.default === "function" ? params.default : () => params.default,
    ...processCreateParams(params)
  });
};
var ZodCatch = class extends ZodType {
  _parse(input) {
    const { ctx } = this._processInputParams(input);
    const newCtx = {
      ...ctx,
      common: {
        ...ctx.common,
        issues: []
      }
    };
    const result = this._def.innerType._parse({
      data: newCtx.data,
      path: newCtx.path,
      parent: {
        ...newCtx
      }
    });
    if (isAsync(result)) {
      return result.then((result2) => {
        return {
          status: "valid",
          value: result2.status === "valid" ? result2.value : this._def.catchValue({
            get error() {
              return new ZodError(newCtx.common.issues);
            },
            input: newCtx.data
          })
        };
      });
    } else {
      return {
        status: "valid",
        value: result.status === "valid" ? result.value : this._def.catchValue({
          get error() {
            return new ZodError(newCtx.common.issues);
          },
          input: newCtx.data
        })
      };
    }
  }
  removeCatch() {
    return this._def.innerType;
  }
};
ZodCatch.create = (type, params) => {
  return new ZodCatch({
    innerType: type,
    typeName: ZodFirstPartyTypeKind.ZodCatch,
    catchValue: typeof params.catch === "function" ? params.catch : () => params.catch,
    ...processCreateParams(params)
  });
};
var ZodNaN = class extends ZodType {
  _parse(input) {
    const parsedType = this._getType(input);
    if (parsedType !== ZodParsedType.nan) {
      const ctx = this._getOrReturnCtx(input);
      addIssueToContext(ctx, {
        code: ZodIssueCode.invalid_type,
        expected: ZodParsedType.nan,
        received: ctx.parsedType
      });
      return INVALID;
    }
    return { status: "valid", value: input.data };
  }
};
ZodNaN.create = (params) => {
  return new ZodNaN({
    typeName: ZodFirstPartyTypeKind.ZodNaN,
    ...processCreateParams(params)
  });
};
var BRAND = /* @__PURE__ */ Symbol("zod_brand");
var ZodBranded = class extends ZodType {
  _parse(input) {
    const { ctx } = this._processInputParams(input);
    const data = ctx.data;
    return this._def.type._parse({
      data,
      path: ctx.path,
      parent: ctx
    });
  }
  unwrap() {
    return this._def.type;
  }
};
var ZodPipeline = class _ZodPipeline extends ZodType {
  _parse(input) {
    const { status, ctx } = this._processInputParams(input);
    if (ctx.common.async) {
      const handleAsync = async () => {
        const inResult = await this._def.in._parseAsync({
          data: ctx.data,
          path: ctx.path,
          parent: ctx
        });
        if (inResult.status === "aborted")
          return INVALID;
        if (inResult.status === "dirty") {
          status.dirty();
          return DIRTY(inResult.value);
        } else {
          return this._def.out._parseAsync({
            data: inResult.value,
            path: ctx.path,
            parent: ctx
          });
        }
      };
      return handleAsync();
    } else {
      const inResult = this._def.in._parseSync({
        data: ctx.data,
        path: ctx.path,
        parent: ctx
      });
      if (inResult.status === "aborted")
        return INVALID;
      if (inResult.status === "dirty") {
        status.dirty();
        return {
          status: "dirty",
          value: inResult.value
        };
      } else {
        return this._def.out._parseSync({
          data: inResult.value,
          path: ctx.path,
          parent: ctx
        });
      }
    }
  }
  static create(a, b) {
    return new _ZodPipeline({
      in: a,
      out: b,
      typeName: ZodFirstPartyTypeKind.ZodPipeline
    });
  }
};
var ZodReadonly = class extends ZodType {
  _parse(input) {
    const result = this._def.innerType._parse(input);
    const freeze2 = (data) => {
      if (isValid(data)) {
        data.value = Object.freeze(data.value);
      }
      return data;
    };
    return isAsync(result) ? result.then((data) => freeze2(data)) : freeze2(result);
  }
  unwrap() {
    return this._def.innerType;
  }
};
ZodReadonly.create = (type, params) => {
  return new ZodReadonly({
    innerType: type,
    typeName: ZodFirstPartyTypeKind.ZodReadonly,
    ...processCreateParams(params)
  });
};
function cleanParams(params, data) {
  const p = typeof params === "function" ? params(data) : typeof params === "string" ? { message: params } : params;
  const p2 = typeof p === "string" ? { message: p } : p;
  return p2;
}
function custom(check, _params = {}, fatal) {
  if (check)
    return ZodAny.create().superRefine((data, ctx) => {
      const r = check(data);
      if (r instanceof Promise) {
        return r.then((r2) => {
          if (!r2) {
            const params = cleanParams(_params, data);
            const _fatal = params.fatal ?? fatal ?? true;
            ctx.addIssue({ code: "custom", ...params, fatal: _fatal });
          }
        });
      }
      if (!r) {
        const params = cleanParams(_params, data);
        const _fatal = params.fatal ?? fatal ?? true;
        ctx.addIssue({ code: "custom", ...params, fatal: _fatal });
      }
      return;
    });
  return ZodAny.create();
}
var late = {
  object: ZodObject.lazycreate
};
var ZodFirstPartyTypeKind;
(function(ZodFirstPartyTypeKind2) {
  ZodFirstPartyTypeKind2["ZodString"] = "ZodString";
  ZodFirstPartyTypeKind2["ZodNumber"] = "ZodNumber";
  ZodFirstPartyTypeKind2["ZodNaN"] = "ZodNaN";
  ZodFirstPartyTypeKind2["ZodBigInt"] = "ZodBigInt";
  ZodFirstPartyTypeKind2["ZodBoolean"] = "ZodBoolean";
  ZodFirstPartyTypeKind2["ZodDate"] = "ZodDate";
  ZodFirstPartyTypeKind2["ZodSymbol"] = "ZodSymbol";
  ZodFirstPartyTypeKind2["ZodUndefined"] = "ZodUndefined";
  ZodFirstPartyTypeKind2["ZodNull"] = "ZodNull";
  ZodFirstPartyTypeKind2["ZodAny"] = "ZodAny";
  ZodFirstPartyTypeKind2["ZodUnknown"] = "ZodUnknown";
  ZodFirstPartyTypeKind2["ZodNever"] = "ZodNever";
  ZodFirstPartyTypeKind2["ZodVoid"] = "ZodVoid";
  ZodFirstPartyTypeKind2["ZodArray"] = "ZodArray";
  ZodFirstPartyTypeKind2["ZodObject"] = "ZodObject";
  ZodFirstPartyTypeKind2["ZodUnion"] = "ZodUnion";
  ZodFirstPartyTypeKind2["ZodDiscriminatedUnion"] = "ZodDiscriminatedUnion";
  ZodFirstPartyTypeKind2["ZodIntersection"] = "ZodIntersection";
  ZodFirstPartyTypeKind2["ZodTuple"] = "ZodTuple";
  ZodFirstPartyTypeKind2["ZodRecord"] = "ZodRecord";
  ZodFirstPartyTypeKind2["ZodMap"] = "ZodMap";
  ZodFirstPartyTypeKind2["ZodSet"] = "ZodSet";
  ZodFirstPartyTypeKind2["ZodFunction"] = "ZodFunction";
  ZodFirstPartyTypeKind2["ZodLazy"] = "ZodLazy";
  ZodFirstPartyTypeKind2["ZodLiteral"] = "ZodLiteral";
  ZodFirstPartyTypeKind2["ZodEnum"] = "ZodEnum";
  ZodFirstPartyTypeKind2["ZodEffects"] = "ZodEffects";
  ZodFirstPartyTypeKind2["ZodNativeEnum"] = "ZodNativeEnum";
  ZodFirstPartyTypeKind2["ZodOptional"] = "ZodOptional";
  ZodFirstPartyTypeKind2["ZodNullable"] = "ZodNullable";
  ZodFirstPartyTypeKind2["ZodDefault"] = "ZodDefault";
  ZodFirstPartyTypeKind2["ZodCatch"] = "ZodCatch";
  ZodFirstPartyTypeKind2["ZodPromise"] = "ZodPromise";
  ZodFirstPartyTypeKind2["ZodBranded"] = "ZodBranded";
  ZodFirstPartyTypeKind2["ZodPipeline"] = "ZodPipeline";
  ZodFirstPartyTypeKind2["ZodReadonly"] = "ZodReadonly";
})(ZodFirstPartyTypeKind || (ZodFirstPartyTypeKind = {}));
var instanceOfType = (cls, params = {
  message: `Input not instance of ${cls.name}`
}) => custom((data) => data instanceof cls, params);
var stringType = ZodString.create;
var numberType = ZodNumber.create;
var nanType = ZodNaN.create;
var bigIntType = ZodBigInt.create;
var booleanType = ZodBoolean.create;
var dateType = ZodDate.create;
var symbolType = ZodSymbol.create;
var undefinedType = ZodUndefined.create;
var nullType = ZodNull.create;
var anyType = ZodAny.create;
var unknownType = ZodUnknown.create;
var neverType = ZodNever.create;
var voidType = ZodVoid.create;
var arrayType = ZodArray.create;
var objectType = ZodObject.create;
var strictObjectType = ZodObject.strictCreate;
var unionType = ZodUnion.create;
var discriminatedUnionType = ZodDiscriminatedUnion.create;
var intersectionType = ZodIntersection.create;
var tupleType = ZodTuple.create;
var recordType = ZodRecord.create;
var mapType = ZodMap.create;
var setType = ZodSet.create;
var functionType = ZodFunction.create;
var lazyType = ZodLazy.create;
var literalType = ZodLiteral.create;
var enumType = ZodEnum.create;
var nativeEnumType = ZodNativeEnum.create;
var promiseType = ZodPromise.create;
var effectsType = ZodEffects.create;
var optionalType = ZodOptional.create;
var nullableType = ZodNullable.create;
var preprocessType = ZodEffects.createWithPreprocess;
var pipelineType = ZodPipeline.create;
var ostring = () => stringType().optional();
var onumber = () => numberType().optional();
var oboolean = () => booleanType().optional();
var coerce = {
  string: ((arg) => ZodString.create({ ...arg, coerce: true })),
  number: ((arg) => ZodNumber.create({ ...arg, coerce: true })),
  boolean: ((arg) => ZodBoolean.create({
    ...arg,
    coerce: true
  })),
  bigint: ((arg) => ZodBigInt.create({ ...arg, coerce: true })),
  date: ((arg) => ZodDate.create({ ...arg, coerce: true }))
};
var NEVER = INVALID;

// src/lib/domain/primitives.ts
var timestampSchema = external_exports.string().datetime();
var idSchema = external_exports.string().min(1).max(160).regex(/^[a-zA-Z0-9][a-zA-Z0-9._:-]*$/).refine((value) => !["__proto__", "prototype", "constructor"].includes(value));

// src/lib/scenes/manifest.ts
var WORLD_WIDTH = 960;
var WORLD_HEIGHT = 540;
var sceneSettingSchema = external_exports.enum(["garden", "courtyard"]);
var scenePinSchema = external_exports.object({ id: idSchema, version: external_exports.number().int().min(1).max(1e6) }).strict();
var regionPreferenceSchema = external_exports.enum([
  "unspecified",
  "europe",
  "north-america",
  "south-america",
  "africa",
  "asia",
  "oceania"
]);
var paletteColorSchema = external_exports.enum([
  "sky",
  "skyLow",
  "grass",
  "grassLight",
  "leaf",
  "leafLight",
  "trunk",
  "wood",
  "wall",
  "stone",
  "water",
  "flower",
  "glow"
]);
var pixelRectSchema = external_exports.object({
  x: external_exports.number().finite().int().min(0),
  y: external_exports.number().finite().int().min(0),
  width: external_exports.number().finite().int().min(1),
  height: external_exports.number().finite().int().min(1),
  color: paletteColorSchema,
  alpha: external_exports.number().finite().min(0).max(1).optional()
}).strict();
var boundsSchema = external_exports.object({
  left: external_exports.number().finite().min(0),
  right: external_exports.number().finite().max(WORLD_WIDTH),
  top: external_exports.number().finite().min(0),
  bottom: external_exports.number().finite().max(WORLD_HEIGHT)
}).strict().refine((b) => b.left < b.right && b.top < b.bottom, "Zones must have positive area.");
var containsPoint = (b, x, y) => x >= b.left && x <= b.right && y >= b.top && y <= b.bottom;
var containsBounds = (outer, inner) => containsPoint(outer, inner.left, inner.top) && containsPoint(outer, inner.right, inner.bottom);
var point = external_exports.object({ id: idSchema, x: external_exports.number().finite(), y: external_exports.number().finite() }).strict();
var layer = (order) => external_exports.object({ order: external_exports.literal(order), assetId: idSchema }).strict();
var sceneManifestSchema = external_exports.object({
  schemaVersion: external_exports.literal(1),
  id: idSchema,
  version: scenePinSchema.shape.version,
  publicSceneId: sceneSettingSchema,
  label: external_exports.string().min(1).max(80),
  representation: external_exports.literal("technical-fixture"),
  provenance: external_exports.object({
    kind: external_exports.literal("existing-authored-geometry"),
    approvedRegionalArt: external_exports.literal(false)
  }).strict(),
  world: external_exports.object({ width: external_exports.literal(WORLD_WIDTH), height: external_exports.literal(WORLD_HEIGHT) }).strict(),
  assets: external_exports.array(
    external_exports.object({
      id: idSchema,
      kind: external_exports.literal("inline-palette-rectangles"),
      rectangles: external_exports.array(pixelRectSchema).min(1).max(512)
    }).strict()
  ).min(3).max(3),
  layers: external_exports.object({ background: layer(0), ground: layer(1), foreground: layer(3) }).strict(),
  depth: external_exports.object({
    order: external_exports.literal(2),
    sort: external_exports.literal("ground-y"),
    actorOffset: external_exports.literal(0.25),
    weatherOrder: external_exports.literal(4)
  }).strict(),
  zones: external_exports.object({
    placement: external_exports.array(boundsSchema).min(1).max(8),
    walkable: external_exports.array(boundsSchema).min(1).max(8)
  }).strict(),
  navigation: external_exports.object({
    mode: external_exports.literal("flight-corridors"),
    groundSlots: external_exports.array(point).min(1).max(128),
    roaming: boundsSchema,
    overflow: external_exports.object({ left: external_exports.number().finite(), right: external_exports.number().finite(), y: external_exports.number().finite() }).strict()
  }).strict()
}).strict().superRefine((manifest, ctx) => {
  const fail = (message) => ctx.addIssue({ code: "custom", message });
  const assets = new Map(manifest.assets.map((asset) => [asset.id, asset]));
  if (assets.size !== manifest.assets.length) fail("Scene asset IDs must be unique.");
  const references = Object.values(manifest.layers).map((value) => value.assetId);
  if (new Set(references).size !== 3 || references.some((id6) => !assets.has(id6)))
    fail("Each required scene layer needs its own valid asset.");
  for (const asset of manifest.assets)
    for (const rect of asset.rectangles)
      if (rect.x + rect.width > manifest.world.width || rect.y + rect.height > manifest.world.height)
        fail("Scene asset pixels must fit the world bounds.");
  const { groundSlots, roaming, overflow } = manifest.navigation;
  if (new Set(groundSlots.map((slot) => slot.id)).size !== groundSlots.length)
    fail("Ground slot IDs must be unique.");
  if (groundSlots.some(
    (slot) => !slot.id.startsWith("ground:") || !manifest.zones.walkable.some((zone) => containsPoint(zone, slot.x, slot.y))
  ))
    fail("Ground slots must be named ground:* and lie in walkable zones.");
  if (!manifest.zones.walkable.some((zone) => containsBounds(zone, roaming)))
    fail("Roaming bounds must fit a walkable zone.");
  if (overflow.left >= overflow.right || !manifest.zones.walkable.some(
    (zone) => containsPoint(zone, overflow.left, overflow.y) && containsPoint(zone, overflow.right, overflow.y)
  ))
    fail("Overflow anchors must fit a walkable zone.");
  if (manifest.zones.placement.some(
    (zone) => overflow.y >= zone.top - 12 && overflow.y <= zone.bottom + 12 && overflow.right >= zone.left - 20 && overflow.left <= zone.right + 20
  ))
    fail("Overflow anchors must remain clear of placeable footprints.");
});

// src/lib/scenes/catalog.ts
function clip(rectangles) {
  return rectangles.map((rect) => ({
    ...rect,
    width: Math.min(rect.width, 960 - rect.x),
    height: Math.min(rect.height, 540 - rect.y)
  })).filter((rect) => rect.width > 0 && rect.height > 0);
}
function fixture(setting) {
  return sceneManifestSchema.parse({
    schemaVersion: 1,
    id: `fixture-${setting}`,
    version: 1,
    publicSceneId: setting,
    label: `${setting === "garden" ? "Garden" : "Courtyard"} technical fixture`,
    representation: "technical-fixture",
    provenance: { kind: "existing-authored-geometry", approvedRegionalArt: false },
    world: { width: 960, height: 540 },
    assets: [
      {
        id: "background",
        kind: "inline-palette-rectangles",
        rectangles: clip(backgroundPrimitives(setting))
      },
      {
        id: "ground",
        kind: "inline-palette-rectangles",
        rectangles: clip(groundPrimitives(setting))
      },
      {
        id: "foreground",
        kind: "inline-palette-rectangles",
        rectangles: clip(foregroundPrimitives())
      }
    ],
    layers: {
      background: { order: 0, assetId: "background" },
      ground: { order: 1, assetId: "ground" },
      foreground: { order: 3, assetId: "foreground" }
    },
    depth: { order: 2, sort: "ground-y", actorOffset: 0.25, weatherOrder: 4 },
    zones: {
      placement: [
        setting === "garden" ? { left: 40, right: 920, top: 340, bottom: 510 } : { left: 90, right: 870, top: 355, bottom: 495 }
      ],
      walkable: [
        { left: 70, right: 890, top: 360, bottom: 510 },
        { left: 70, right: 890, top: 520, bottom: 532 }
      ]
    },
    navigation: {
      mode: "flight-corridors",
      groundSlots: Array.from({ length: 24 }, (_, i) => ({
        id: `ground:${Math.floor(i / 8)}:${i % 8}`,
        x: 100 + i % 8 * 108,
        y: 370 + Math.floor(i / 8) * 64
      })),
      roaming: { left: 70, right: 890, top: 375, bottom: 507 },
      overflow: { left: 90, right: 870, y: 525 }
    }
  });
}
function freeze(value) {
  if (value && typeof value === "object") {
    for (const child of Object.values(value)) freeze(child);
    Object.freeze(value);
  }
  return value;
}
var fixtures = freeze({ garden: fixture("garden"), courtyard: fixture("courtyard") });
var SCENE_CATALOG = Object.freeze(Object.values(fixtures));
var fixtureScene = (setting) => fixtures[setting];
var legacyScenePin = (setting) => ({
  id: fixtures[setting].id,
  version: 1
});
function resolveScene(setting, pin, catalog = SCENE_CATALOG) {
  const requested = pin ?? legacyScenePin(setting);
  const candidates = catalog.filter(
    (entry) => !!entry && typeof entry === "object" && "id" in entry && "version" in entry && entry.id === requested.id && entry.version === requested.version
  );
  const parsed = candidates.length === 1 ? sceneManifestSchema.safeParse(candidates[0]) : void 0;
  const ready = scenePinSchema.safeParse(requested).success && parsed?.success && parsed.data.publicSceneId === setting;
  const manifest = ready && parsed?.success ? parsed.data : fixtureScene(setting);
  const status = ready ? "ready" : "unavailable";
  return {
    requested: { ...requested },
    manifest,
    status,
    message: ready ? `${manifest.label}. Regional artwork is not reviewed.` : "Selected scene manifest is unavailable or invalid. Showing the existing technical fixture; your saved scene selection is retained.",
    key: JSON.stringify([requested, status, manifest])
  };
}

// src/lib/server/storage/repository.ts
import { DatabaseSync } from "node:sqlite";
import { randomUUID, createHash } from "node:crypto";
import { mkdirSync } from "node:fs";
import { dirname } from "node:path";

// src/lib/assets/manifest-v2.ts
var animationStates = [
  "idle",
  "moving",
  "perching",
  "singing",
  "feeding",
  "bathing",
  "sleeping",
  "playing",
  "nesting"
];
var identifier = external_exports.string().min(1).max(160);
var integer = external_exports.number().int().nonnegative();
var animationPinSchema = external_exports.object({
  jobId: identifier,
  artifactId: identifier,
  version: external_exports.number().int().positive().max(Number.MAX_SAFE_INTEGER),
  contentDigest: external_exports.string().regex(/^[a-f0-9]{64}$/)
}).strict();
var rectangle = external_exports.object({
  x: integer,
  y: integer,
  width: external_exports.number().int().min(1).max(256),
  height: external_exports.number().int().min(1).max(256),
  color: external_exports.number().int().min(0).max(16777215)
}).strict();
var clip2 = external_exports.object({
  frames: external_exports.array(integer).min(1).max(256),
  ticksPerFrame: external_exports.number().int().min(1).max(300),
  loop: external_exports.boolean(),
  /** Optional authored pose transform, also frozen to the first pose in quiet mode. */
  rotations: external_exports.array(external_exports.number().min(-0.5).max(0.5)).max(256).optional()
}).strict();
var speciesManifestV2Schema = external_exports.object({
  schemaVersion: external_exports.literal(2),
  speciesId: identifier,
  representation: external_exports.string().min(1).max(200),
  fixture: external_exports.boolean(),
  taxonFidelityReviewed: external_exports.boolean(),
  format: external_exports.literal("pixel-rects"),
  canvas: external_exports.object({
    width: external_exports.number().int().min(1).max(256),
    height: external_exports.number().int().min(1).max(256),
    anchorX: integer,
    anchorY: integer
  }).strict(),
  frames: external_exports.array(external_exports.array(rectangle).min(1).max(4096)).min(1).max(64),
  clips: external_exports.object(
    Object.fromEntries(
      animationStates.map((state) => [state, state === "idle" ? clip2 : clip2.optional()])
    )
  ).strict(),
  provenance: external_exports.object({
    source: external_exports.enum(["deterministic_fixture", "provider", "user_upload"]),
    creator: identifier,
    sourceVersion: identifier,
    references: external_exports.array(identifier).max(32),
    license: external_exports.string().min(1).max(200),
    usage: external_exports.enum(["development-only", "cleared"]),
    attribution: external_exports.string().min(1).max(300)
  }).strict()
}).strict().superRefine((value, context) => {
  const fail = (message) => context.addIssue({ code: "custom", message });
  if (value.canvas.anchorX > value.canvas.width || value.canvas.anchorY > value.canvas.height)
    fail("Anchor exceeds canvas bounds");
  if (value.frames.reduce((sum, frame) => sum + frame.length, 0) > 16384)
    fail("Manifest exceeds total rectangle budget");
  if (value.frames.some(
    (frame) => frame.some(
      (rect) => rect.x + rect.width > value.canvas.width || rect.y + rect.height > value.canvas.height
    )
  ))
    fail("Frame exceeds canvas bounds");
  for (const entry of Object.values(value.clips)) {
    if (!entry) continue;
    if (entry.frames.some((index) => index >= value.frames.length))
      fail("Clip frame index exceeds frame count");
    if (entry.rotations && entry.rotations.length !== entry.frames.length)
      fail("Clip pose count must match frames");
  }
  if (value.fixture && (value.taxonFidelityReviewed || value.provenance.source !== "deterministic_fixture" || value.provenance.usage !== "development-only"))
    fail("Fixture cannot claim fidelity review or cleared production usage");
  if (!value.fixture && (!value.taxonFidelityReviewed || value.provenance.source === "deterministic_fixture" || value.provenance.usage !== "cleared"))
    fail("Non-fixture art requires fidelity review and cleared usage");
});

// src/lib/assets/catalog-pin.ts
var catalogPinSchema = external_exports.object({
  catalogKey: external_exports.string().regex(/^[a-f0-9]{64}$/),
  releaseVersion: external_exports.number().int().min(1).max(Number.MAX_SAFE_INTEGER),
  renderSha256: external_exports.string().regex(/^[a-f0-9]{64}$/)
}).strict();

// src/lib/domain/evidence.ts
var evidenceValueSchema = external_exports.object({
  speciesId: idSchema,
  observedAt: timestampSchema.nullable()
}).strict();
var evidenceRevisionSchema = evidenceValueSchema.extend({
  correctionId: external_exports.string().uuid().nullable()
}).strict();
var manualFindingSchema = external_exports.object({
  schemaVersion: external_exports.literal(1),
  id: external_exports.string().uuid(),
  speciesId: idSchema,
  observedAt: timestampSchema.nullable(),
  note: external_exports.string().max(1e3)
}).strict();
var correctionInputSchema = external_exports.object({
  schemaVersion: external_exports.literal(1),
  id: external_exports.string().uuid(),
  eventId: idSchema,
  expected: evidenceRevisionSchema,
  replacement: evidenceValueSchema,
  reason: external_exports.string().min(1).max(500).regex(/\S/, "Explain the correction.")
}).strict();
var correctionRecordSchema = correctionInputSchema.extend({
  recordedAt: timestampSchema
}).strict();
var findingCommandSchema = external_exports.discriminatedUnion("action", [
  external_exports.object({ action: external_exports.literal("manual-finding"), finding: manualFindingSchema }).strict(),
  external_exports.object({
    action: external_exports.literal("correct-events"),
    corrections: external_exports.array(correctionInputSchema).min(1).max(100)
  }).strict()
]);
var effectiveEvidenceSchema = evidenceRevisionSchema.extend({ eventId: idSchema }).strict();
var sameValue = (a, b) => a.speciesId === b.speciesId && (a.observedAt === b.observedAt || a.observedAt !== null && b.observedAt !== null && Date.parse(a.observedAt) === Date.parse(b.observedAt));
var sameRevision = (a, b) => a.correctionId === b.correctionId && sameValue(a, b);

// src/lib/domain/validation-error.ts
var messages = {
  objectPlacement: "Objects must fit inside the yard ground area without overlapping other objects.",
  sceneCapacity: "This yard has no collision-free placement for all objects.",
  legacySpeciesIdentity: "Legacy species key mismatch",
  legacyArtworkIdentity: "Legacy artwork identity mismatch"
};
var YardValidationError = class extends Error {
  code = "INVALID";
  constructor(reason) {
    super(messages[reason]);
    this.name = "YardValidationError";
  }
};

// src/lib/domain/scene.ts
var sceneManifestOf = (input) => typeof input === "string" ? fixtureScene(input) : input;
var MAX_OBJECTS = 12;
var OBJECT_CLEARANCE = 8;
var objectKindSchema = external_exports.enum(["perch", "feeder", "bath", "nest"]);
var OBJECT_CATALOG = {
  perch: {
    label: "Perch",
    width: 96,
    depth: 30,
    height: 130,
    slots: [
      { id: "left", affordance: "perch", dx: -25, dy: -115 },
      { id: "right", affordance: "perch", dx: 25, dy: -115, capability: "play" }
    ]
  },
  feeder: {
    label: "Feeder",
    width: 84,
    depth: 46,
    height: 74,
    slots: [
      { id: "left", affordance: "feed", dx: -18, dy: -24 },
      { id: "right", affordance: "feed", dx: 18, dy: -24 }
    ]
  },
  bath: {
    label: "Birdbath",
    width: 100,
    depth: 54,
    height: 80,
    slots: [
      { id: "left", affordance: "bath", dx: -18, dy: -68 },
      { id: "right", affordance: "bath", dx: 18, dy: -68 }
    ]
  },
  nest: {
    label: "Nest",
    width: 72,
    depth: 36,
    height: 50,
    slots: [{ id: "center", affordance: "nest", dx: 0, dy: -30, capability: "nest-building" }]
  }
};
var yardObjectSchema = external_exports.object({
  id: idSchema,
  kind: objectKindSchema,
  x: external_exports.number().finite().min(0).max(WORLD_WIDTH),
  y: external_exports.number().finite().min(0).max(WORLD_HEIGHT)
}).strict();
var yardObjectsSchema = external_exports.array(yardObjectSchema).max(MAX_OBJECTS).superRefine((objects, ctx) => {
  if (new Set(objects.map((object) => object.id)).size !== objects.length)
    ctx.addIssue({ code: "custom", message: "Yard object IDs must be unique." });
});
var placementSnapshotSchema = external_exports.object({
  scene: sceneSettingSchema,
  scenePin: scenePinSchema.nullable().optional(),
  objects: yardObjectsSchema
}).strict();
function placementKey(scene, objects, pin) {
  return JSON.stringify([
    scene,
    pin ?? legacyScenePin(scene),
    [...objects].sort((a, b) => a.id.localeCompare(b.id)).map(({ id: id6, kind, x, y }) => [id6, kind, x, y])
  ]);
}
var PLACEMENT_BOUNDS = {
  garden: placementBounds("garden"),
  courtyard: placementBounds("courtyard")
};
function placementBounds(setting) {
  const first = fixtureScene(setting).zones.placement[0];
  if (!first) throw new Error("Fixture scene requires a placement zone");
  return first;
}
function objectFootprint(object) {
  const definition = OBJECT_CATALOG[object.kind];
  return {
    left: object.x - definition.width / 2,
    right: object.x + definition.width / 2,
    top: object.y - definition.depth / 2,
    bottom: object.y + definition.depth / 2
  };
}
function objectsOverlap(first, second) {
  const a = objectFootprint(first), b = objectFootprint(second);
  return a.left < b.right + OBJECT_CLEARANCE && a.right + OBJECT_CLEARANCE > b.left && a.top < b.bottom + OBJECT_CLEARANCE && a.bottom + OBJECT_CLEARANCE > b.top;
}
function isPlacementValid(object, objects, setting) {
  const manifest = sceneManifestOf(setting), bounds = objectFootprint(object);
  return manifest.zones.placement.some((area) => containsBounds(area, bounds)) && object.y - OBJECT_CATALOG[object.kind].height >= 24 && !objects.some((other) => other.id !== object.id && objectsOverlap(object, other));
}
function validateObjects(input, setting) {
  const objects = yardObjectsSchema.parse(input);
  for (const object of objects)
    if (!isPlacementValid(object, objects, setting))
      throw new YardValidationError("objectPlacement");
  return objects;
}
function defaultObjects(setting = "garden") {
  const objects = [
    { id: "fixture-perch", kind: "perch", x: 180, y: 420 },
    { id: "fixture-feeder", kind: "feeder", x: 400, y: 465 },
    { id: "fixture-bath", kind: "bath", x: 700, y: 445 },
    { id: "fixture-nest", kind: "nest", x: 820, y: 475 }
  ];
  return validateObjects(objects, setting);
}
function placementCandidates(kind, setting, desired) {
  const definition = OBJECT_CATALOG[kind];
  const candidates = [];
  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
  for (const area of sceneManifestOf(setting).zones.placement) {
    const minX = area.left + definition.width / 2, maxX = area.right - definition.width / 2;
    const minY = area.top + definition.depth / 2, maxY = area.bottom - definition.depth / 2;
    if (minX > maxX || minY > maxY) continue;
    candidates.push({ x: clamp(desired.x, minX, maxX), y: clamp(desired.y, minY, maxY) });
    for (let y = minY; y <= maxY; y += 8)
      for (let x = minX; x <= maxX; x += 8) candidates.push({ x, y });
  }
  return candidates.sort(
    (a, b) => (a.x - desired.x) ** 2 + (a.y - desired.y) ** 2 - ((b.x - desired.x) ** 2 + (b.y - desired.y) ** 2) || a.y - b.y || a.x - b.x
  );
}
function findObjectPlacement(kind, objects, setting, desired = { x: WORLD_WIDTH / 2, y: 430 }) {
  objectKindSchema.parse(kind);
  for (const point3 of placementCandidates(kind, setting, desired)) {
    const candidate = { id: "placement-candidate", kind, ...point3 };
    if (isPlacementValid(
      candidate,
      objects.filter((object) => object.id !== "placement-candidate"),
      setting
    ) && !objects.some((other) => objectsOverlap(candidate, other)))
      return point3;
  }
  return null;
}
function reanchorObjects(input, setting) {
  const objects = yardObjectsSchema.parse(input);
  let placed = objects.filter((object) => isPlacementValid(object, objects, setting));
  const retained = new Set(placed.map((object) => object.id));
  const ordered = [...objects].sort(
    (a, b) => OBJECT_CATALOG[b.kind].width * OBJECT_CATALOG[b.kind].depth - OBJECT_CATALOG[a.kind].width * OBJECT_CATALOG[a.kind].depth || a.id.localeCompare(b.id)
  );
  for (const object of ordered) {
    if (retained.has(object.id)) continue;
    const position = findObjectPlacement(object.kind, placed, setting, object);
    if (!position) {
      placed = [];
      break;
    }
    placed.push({ ...object, ...position });
  }
  if (placed.length !== objects.length) {
    const areas = sceneManifestOf(setting).zones.placement;
    const width = Math.max(...Object.values(OBJECT_CATALOG).map((definition) => definition.width));
    const depth = Math.max(...Object.values(OBJECT_CATALOG).map((definition) => definition.depth));
    const cells = [];
    for (const bounds of areas)
      for (let y = bounds.top + depth / 2; y <= bounds.bottom - depth / 2; y += depth + OBJECT_CLEARANCE)
        for (let x = bounds.left + width / 2; x <= bounds.right - width / 2; x += width + OBJECT_CLEARANCE)
          cells.push({ x, y });
    for (const object of ordered) {
      cells.sort(
        (a, b) => (a.x - object.x) ** 2 + (a.y - object.y) ** 2 - ((b.x - object.x) ** 2 + (b.y - object.y) ** 2) || a.y - b.y || a.x - b.x
      );
      const position = cells.find(
        (point3) => isPlacementValid({ ...object, ...point3 }, placed, setting)
      );
      if (!position) throw new YardValidationError("sceneCapacity");
      placed.push({ ...object, ...position });
    }
  }
  const byId = new Map(placed.map((object) => [object.id, object]));
  return validateObjects(
    objects.map((object) => byId.get(object.id)),
    setting
  );
}

// src/lib/domain/object-inventory.ts
var FREE_FIXTURES_PER_KIND = 3;
var MAX_OBJECT_OPERATION_RECEIPTS = 4096;
var objectInventorySchema = external_exports.object({
  version: external_exports.literal(1),
  owned: external_exports.object({
    perch: external_exports.number().int().min(0).max(MAX_OBJECTS),
    feeder: external_exports.number().int().min(0).max(MAX_OBJECTS),
    bath: external_exports.number().int().min(0).max(MAX_OBJECTS),
    nest: external_exports.number().int().min(0).max(MAX_OBJECTS)
  }).strict()
}).strict();
var objectOperationReceiptSchema = external_exports.object({
  requestId: external_exports.string().uuid(),
  commandDigest: external_exports.string().regex(/^[a-f0-9]{64}$/),
  resultObjectId: idSchema
}).strict();
var objectOperationReceiptsSchema = external_exports.array(objectOperationReceiptSchema).max(MAX_OBJECT_OPERATION_RECEIPTS).superRefine((receipts, context) => {
  if (new Set(receipts.map((receipt) => receipt.requestId)).size !== receipts.length)
    context.addIssue({ code: "custom", message: "Object operation request IDs must be unique." });
});
var objectInventoryCommandSchema = external_exports.object({
  action: external_exports.literal("object-inventory"),
  requestId: external_exports.string().uuid(),
  expected: placementSnapshotSchema,
  payload: external_exports.discriminatedUnion("operation", [
    external_exports.object({ operation: external_exports.literal("place"), kind: objectKindSchema }).strict(),
    external_exports.object({ operation: external_exports.literal("return"), objectId: idSchema }).strict(),
    external_exports.object({
      operation: external_exports.literal("move"),
      objectId: idSchema,
      x: external_exports.number().finite(),
      y: external_exports.number().finite()
    }).strict()
  ])
}).strict();
function starterInventory(objects) {
  const placed = yardObjectsSchema.parse(objects);
  const owned = { perch: 3, feeder: 3, bath: 3, nest: 3 };
  for (const kind of objectKindSchema.options)
    owned[kind] = Math.max(
      FREE_FIXTURES_PER_KIND,
      placed.filter((item) => item.kind === kind).length
    );
  return { version: 1, owned };
}
function inventoryIssues(inventory, objects) {
  return objectKindSchema.options.filter((kind) => availableStock(inventory, objects, kind) < 0).map((kind) => `Placed ${kind} objects exceed owned stock.`);
}
function availableStock(inventory, objects, kind) {
  return inventory.owned[kind] - objects.filter((object) => object.kind === kind).length;
}

// src/lib/weather/contracts.ts
var weatherConditionSchema = external_exports.enum(["clear", "cloudy", "rain", "snow"]);
var weatherSettingsSchema = external_exports.object({
  mode: external_exports.enum(["simulated", "manual", "real"]),
  manual: external_exports.object({
    condition: weatherConditionSchema,
    hour: external_exports.number().int().min(0).max(23)
  }).strict(),
  simulation: external_exports.object({
    seed: external_exports.number().int().safe(),
    dayLengthSeconds: external_exports.number().int().min(120).max(86400),
    epoch: external_exports.string().datetime()
  }).strict()
}).strict();
function defaultWeatherSettings() {
  return {
    mode: "simulated",
    manual: { condition: "clear", hour: 12 },
    simulation: {
      seed: 17,
      dayLengthSeconds: 600,
      epoch: "2026-01-01T00:00:00Z"
    }
  };
}

// src/lib/domain/yard.ts
var jsonValueSchema = external_exports.lazy(
  () => external_exports.union([
    external_exports.string(),
    external_exports.number().finite(),
    external_exports.boolean(),
    external_exports.null(),
    external_exports.array(jsonValueSchema),
    external_exports.record(jsonValueSchema)
  ])
);
var speciesSchema = external_exports.object({
  id: idSchema,
  commonName: external_exports.string().min(1).max(120),
  scientificName: external_exports.string().min(3).max(160),
  description: external_exports.string().max(1e3).optional(),
  referencePhoto: external_exports.record(jsonValueSchema).optional()
}).strict();
var sourceSchema = external_exports.object({
  kind: external_exports.enum(["fixture", "manual", "model", "external"]),
  label: external_exports.string().min(1).max(120),
  sourceEventId: idSchema,
  provider: external_exports.string().min(1).max(100).optional(),
  modelVersion: external_exports.string().max(100).optional()
}).strict();
var identificationSchema = external_exports.object({
  schemaVersion: external_exports.literal(2),
  id: idSchema,
  species: speciesSchema,
  observedAt: timestampSchema.nullable(),
  ingestedAt: timestampSchema,
  source: sourceSchema,
  confidence: external_exports.number().min(0).max(1).optional(),
  recordingId: idSchema.optional(),
  /** Private evidence only. Never copy this object into a public projection. */
  metadata: external_exports.record(jsonValueSchema).optional()
}).strict();
var importEventSchema = identificationSchema.omit({ ingestedAt: true }).extend({ ingestedAt: timestampSchema.optional() });
var hasControlCharacters = (value) => Array.from(value).some(
  (character) => character.charCodeAt(0) < 32 || character.charCodeAt(0) === 127
);
var localImageSchema = external_exports.string().max(15e5).refine(
  (value) => value.startsWith("/") && !value.startsWith("//") && !/[\\\s]/.test(value) && !hasControlCharacters(value) || /^data:image\/(png|jpeg|webp);base64,[a-zA-Z0-9+/=]+$/.test(value),
  "Use a bundled image path or embedded PNG, JPEG or WebP image; remote image requests are disabled."
);
var artworkObjectSchema = external_exports.object({
  id: idSchema,
  speciesId: idSchema,
  version: external_exports.number().int().positive(),
  status: external_exports.enum(["fixture", "reviewed"]),
  /** Optional exact pipeline artifact; old backups and image-only art remain valid. */
  animationPin: animationPinSchema.optional(),
  /** Exact generic shared release; never a private job or an individual bird identity. */
  catalogPin: catalogPinSchema.optional(),
  imageUrl: localImageSchema,
  sha256: external_exports.string().regex(/^[a-f0-9]{64}$/).optional(),
  representation: external_exports.string().min(1).max(200),
  provenance: external_exports.record(jsonValueSchema),
  /** Only explicit catalog keys can cross the public boundary; URLs cannot. */
  catalogKey: external_exports.enum(["fixture-robin", "fixture-sparrow", "fixture-bluejay"]).optional()
}).strict();
var artworkSchema = artworkObjectSchema.superRefine((artwork, context) => {
  if (artwork.catalogPin && (artwork.animationPin || artwork.catalogKey))
    context.addIssue({
      code: "custom",
      message: "Shared, private and bundled asset pins cannot be mixed."
    });
});
var birdInstanceSchema = external_exports.object({
  id: idSchema,
  speciesId: idSchema,
  name: external_exports.string().trim().min(1).max(60).nullable(),
  lifecycle: external_exports.enum(["temporary", "permanent", "expired"]),
  createdAt: timestampSchema,
  expiresAt: timestampSchema.nullable(),
  promotedAt: timestampSchema.nullable(),
  artworkId: idSchema.nullable(),
  originEventId: idSchema.nullable()
}).strict();
var collectionEntrySchema = external_exports.object({ id: idSchema, speciesId: idSchema, collectedAt: timestampSchema }).strict();
var preferencesSchema = external_exports.object({
  palette: external_exports.enum(["twilight", "fieldnotes", "moonlit"]),
  scene: sceneSettingSchema,
  scenePin: scenePinSchema.nullable().default(null),
  regionPreference: regionPreferenceSchema.default("unspecified"),
  reducedMotion: external_exports.boolean(),
  /** Provisional development default; changing it affects future imports only. */
  visitorTtlHours: external_exports.number().int().min(1).max(24 * 90)
}).strict();
var preferencesPatchSchema = preferencesSchema.partial();
var defaultPreferences = () => ({
  palette: "twilight",
  scene: "garden",
  scenePin: null,
  regionPreference: "unspecified",
  reducedMotion: false,
  visitorTtlHours: 24
});
var environmentSchema = external_exports.object({
  version: external_exports.literal(1),
  objects: yardObjectsSchema,
  weather: weatherSettingsSchema,
  inventory: objectInventorySchema,
  objectReceipts: objectOperationReceiptsSchema
}).strict();
var persistedEnvironmentSchema = environmentSchema.extend({
  inventory: objectInventorySchema.optional(),
  objectReceipts: objectOperationReceiptsSchema.optional()
}).transform((environment) => ({
  ...environment,
  inventory: environment.inventory ?? starterInventory(environment.objects),
  objectReceipts: environment.objectReceipts ?? []
}));
var defaultEnvironment = () => ({
  version: 1,
  objects: defaultObjects(),
  weather: defaultWeatherSettings(),
  inventory: starterInventory(defaultObjects()),
  objectReceipts: []
});
var yardDataSchema = external_exports.object({
  version: external_exports.literal(2),
  species: external_exports.array(speciesSchema),
  events: external_exports.array(identificationSchema),
  /** Additive v2 extension; raw events never change when corrections are appended. */
  corrections: external_exports.array(correctionRecordSchema).max(1e4).default([]),
  collection: external_exports.array(collectionEntrySchema),
  birds: external_exports.array(birdInstanceSchema),
  artworks: external_exports.array(artworkSchema),
  preferences: preferencesSchema,
  /** Additive v2 extension: older persisted yards/backups receive fresh, stable defaults. */
  environment: persistedEnvironmentSchema.default(defaultEnvironment)
}).strict().superRefine((state, ctx) => {
  const fail = (message) => ctx.addIssue({ code: "custom", message });
  for (const issue of inventoryIssues(state.environment.inventory, state.environment.objects))
    fail(issue);
  try {
    validateObjects(
      state.environment.objects,
      resolveScene(state.preferences.scene, state.preferences.scenePin).manifest
    );
  } catch {
    fail("Invalid yard object placement for this scene.");
  }
  for (const [label2, values] of Object.entries({
    species: state.species,
    events: state.events,
    corrections: state.corrections,
    collection: state.collection,
    birds: state.birds,
    artworks: state.artworks
  })) {
    if (new Set(values.map((value) => value.id)).size !== values.length)
      fail(`Duplicate ${label2} ID`);
  }
  const species = new Map(state.species.map((s) => [s.id, s]));
  const art = new Map(state.artworks.map((a) => [a.id, a]));
  if (new Set(state.species.map((s) => s.scientificName.toLowerCase())).size !== state.species.length)
    fail("Duplicate taxon identity");
  if (new Set(state.events.map(sourceEventKey)).size !== state.events.length)
    fail("Duplicate source event identity");
  if (new Set(state.collection.map((entry) => entry.speciesId)).size !== state.collection.length)
    fail("Duplicate collection species");
  if (new Set(state.artworks.map((a) => `${a.speciesId}:${a.version}`)).size !== state.artworks.length)
    fail("Duplicate artwork version");
  for (const event of state.events)
    if (species.get(event.species.id)?.scientificName !== event.species.scientificName)
      fail("Evidence taxon mismatch");
  const revisions = new Map(
    state.events.map((event) => [
      event.id,
      {
        eventId: event.id,
        correctionId: null,
        speciesId: event.species.id,
        observedAt: event.observedAt
      }
    ])
  );
  for (const correction of state.corrections) {
    const previous = revisions.get(correction.eventId);
    if (!previous || !sameRevision(previous, correction.expected))
      fail("Correction history must be an unbroken append-only chain.");
    if (!species.has(correction.replacement.speciesId)) fail("Corrected species missing");
    revisions.set(correction.eventId, {
      eventId: correction.eventId,
      correctionId: correction.id,
      ...correction.replacement
    });
  }
  for (const entry of [...state.collection, ...state.birds, ...state.artworks])
    if (!species.has(entry.speciesId)) fail("Referenced species missing");
  for (const bird of state.birds) {
    if (bird.artworkId && art.get(bird.artworkId)?.speciesId !== bird.speciesId)
      fail("Pinned artwork taxon mismatch");
    if (bird.originEventId && !state.events.some((event) => event.id === bird.originEventId))
      fail("Origin event missing");
    if (bird.lifecycle === "permanent" && bird.expiresAt !== null)
      fail("Permanent birds cannot expire");
    if (bird.lifecycle !== "permanent" && bird.expiresAt === null)
      fail("Temporary birds require expiry");
  }
});
var findingSchema = external_exports.object({
  id: external_exports.string().min(1).max(168),
  speciesId: idSchema,
  eventIds: external_exports.array(idSchema).min(1),
  evidenceCount: external_exports.number().int().positive().max(Number.MAX_SAFE_INTEGER),
  firstObservedAt: timestampSchema.nullable(),
  lastObservedAt: timestampSchema.nullable(),
  sourceKinds: external_exports.array(sourceSchema.shape.kind).min(1),
  hasUnknownTime: external_exports.boolean()
}).strict();
var snapshotProjectionSchema = external_exports.object({
  findings: external_exports.array(findingSchema),
  effectiveEvidence: external_exports.array(effectiveEvidenceSchema)
}).strict();
var emptyYard = () => ({
  version: 2,
  species: [],
  events: [],
  corrections: [],
  collection: [],
  birds: [],
  artworks: [],
  preferences: defaultPreferences(),
  environment: defaultEnvironment()
});
function sourceEventKey(event) {
  return JSON.stringify([
    event.source.kind,
    event.source.provider ?? "",
    event.source.sourceEventId
  ]);
}
function canonicalJson(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (value && typeof value === "object")
    return `{${Object.keys(value).filter((key) => value[key] !== void 0).sort().map(
      (key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`
    ).join(",")}}`;
  return JSON.stringify(value) ?? "null";
}
function evidenceFingerprint(event) {
  const evidence2 = Object.fromEntries(
    Object.entries(event).filter(([key]) => key !== "ingestedAt")
  );
  return canonicalJson(evidence2);
}
function effectiveEvidenceOf(data) {
  const latest = new Map(data.corrections.map((correction) => [correction.eventId, correction]));
  return data.events.map((event) => {
    const correction = latest.get(event.id);
    return {
      eventId: event.id,
      correctionId: correction?.id ?? null,
      ...correction?.replacement ?? { speciesId: event.species.id, observedAt: event.observedAt }
    };
  });
}
function snapshotOf(data, now) {
  const groups = /* @__PURE__ */ new Map();
  const effectiveEvidence = effectiveEvidenceOf(data);
  const effective = new Map(effectiveEvidence.map((entry) => [entry.eventId, entry]));
  for (const event of data.events) {
    const value = effective.get(event.id);
    const finding = groups.get(value.speciesId) ?? {
      id: `finding:${value.speciesId}`,
      speciesId: value.speciesId,
      eventIds: [],
      evidenceCount: 0,
      firstObservedAt: null,
      lastObservedAt: null,
      sourceKinds: [],
      hasUnknownTime: false
    };
    finding.eventIds.push(event.id);
    finding.evidenceCount++;
    if (!finding.sourceKinds.includes(event.source.kind))
      finding.sourceKinds.push(event.source.kind);
    if (value.observedAt === null) finding.hasUnknownTime = true;
    else {
      if (!finding.firstObservedAt || Date.parse(value.observedAt) < Date.parse(finding.firstObservedAt))
        finding.firstObservedAt = value.observedAt;
      if (!finding.lastObservedAt || Date.parse(value.observedAt) > Date.parse(finding.lastObservedAt))
        finding.lastObservedAt = value.observedAt;
    }
    groups.set(value.speciesId, finding);
  }
  return {
    ...data,
    effectiveEvidence,
    birds: data.birds.map(
      (bird) => bird.lifecycle === "temporary" && Date.parse(bird.expiresAt) <= Date.parse(now) ? { ...bird, lifecycle: "expired" } : bird
    ),
    findings: [...groups.values()]
  };
}
var yardSnapshotSchema = yardDataSchema.innerType().extend({
  ...snapshotProjectionSchema.shape,
  environment: environmentSchema,
  corrections: yardDataSchema.innerType().shape.corrections.removeDefault(),
  preferences: preferencesSchema.extend({
    scenePin: preferencesSchema.shape.scenePin.removeDefault(),
    regionPreference: preferencesSchema.shape.regionPreference.removeDefault()
  }).strict()
}).strict().superRefine((snapshot, context) => {
  const { findings, effectiveEvidence, ...raw2 } = snapshot;
  const parsed = yardDataSchema.safeParse(raw2);
  if (!parsed.success) {
    for (const issue of parsed.error.issues) context.addIssue(issue);
    return;
  }
  const expected = snapshotOf(parsed.data, "1970-01-01T00:00:00.000Z");
  if (canonicalJson(findings) !== canonicalJson(expected.findings))
    context.addIssue({
      code: "custom",
      path: ["findings"],
      message: "Findings do not match saved evidence."
    });
  if (canonicalJson(effectiveEvidence) !== canonicalJson(expected.effectiveEvidence))
    context.addIssue({
      code: "custom",
      path: ["effectiveEvidence"],
      message: "Effective evidence does not match correction history."
    });
});
var backupSchema = external_exports.object({
  format: external_exports.literal("chirpneighbors-yard"),
  version: external_exports.literal(2),
  exportedAt: timestampSchema,
  data: yardDataSchema
}).strict();
var displayCatalog = {
  "cn-species-erithacus-rubecula": {
    commonName: "European Robin",
    scientificName: "Erithacus rubecula",
    catalogKey: "fixture-robin"
  },
  "cn-species-passer-domesticus": {
    commonName: "House Sparrow",
    scientificName: "Passer domesticus",
    catalogKey: "fixture-sparrow"
  },
  "cn-species-cyanocitta-cristata": {
    commonName: "Blue Jay",
    scientificName: "Cyanocitta cristata",
    catalogKey: "fixture-bluejay"
  }
};
function catalogEntry(speciesId) {
  return Object.hasOwn(displayCatalog, speciesId) ? displayCatalog[speciesId] : void 0;
}
function availableSpecies(data) {
  const choices = data.species.map(({ id: id6, commonName, scientificName }) => ({
    id: id6,
    commonName,
    scientificName
  }));
  for (const [id6, species] of Object.entries(displayCatalog)) {
    if (!choices.some(
      (entry) => entry.id === id6 || entry.scientificName.toLowerCase() === species.scientificName.toLowerCase()
    ))
      choices.push({ id: id6, commonName: species.commonName, scientificName: species.scientificName });
  }
  return choices;
}
var publicYardProjectionSchema = external_exports.object({
  version: external_exports.literal(1),
  viewOnly: external_exports.literal(true),
  scene: sceneSettingSchema,
  palette: preferencesSchema.shape.palette,
  birds: external_exports.array(
    external_exports.object({
      displayKey: external_exports.string().regex(/^bird-[1-9][0-9]*$/),
      commonName: speciesSchema.shape.commonName,
      scientificName: speciesSchema.shape.scientificName.nullable(),
      catalogKey: artworkObjectSchema.shape.catalogKey.unwrap().nullable()
    }).strict()
  )
}).strict();

// src/lib/domain/migration.ts
var legacyPhoto = external_exports.object({
  id: idSchema,
  speciesId: idSchema,
  creator: external_exports.string().min(1),
  sourceUrl: external_exports.string().url(),
  license: external_exports.enum(["CC0-1.0", "CC-BY-4.0", "CC-BY-SA-4.0", "user-owned"]),
  licenseUrl: external_exports.string().url(),
  verifiedAt: timestampSchema,
  representation: external_exports.string().min(1),
  imageUrl: external_exports.string().optional(),
  sha256: external_exports.string().optional()
}).strict();
var legacySpecies = external_exports.object({
  id: idSchema,
  commonName: external_exports.string().min(1).max(120),
  scientificName: external_exports.string().min(3).max(160),
  description: external_exports.string().max(1e3).optional(),
  referencePhoto: legacyPhoto.optional()
}).strict();
var legacySchema = external_exports.object({
  version: external_exports.literal(1),
  species: external_exports.record(legacySpecies),
  identifications: external_exports.array(
    external_exports.object({
      schemaVersion: external_exports.literal(1),
      id: idSchema,
      species: legacySpecies,
      observedAt: timestampSchema,
      source: external_exports.object({
        kind: external_exports.enum(["audio", "manual", "import", "demo"]),
        label: external_exports.string().min(1).max(120)
      }).strict(),
      confidence: external_exports.number().min(0).max(1).optional(),
      recordingUrl: external_exports.string().optional()
    }).strict()
  ),
  residents: external_exports.array(
    external_exports.object({
      id: idSchema,
      speciesId: idSchema,
      savedAt: timestampSchema,
      artworkId: idSchema.nullable()
    }).strict()
  ),
  artworks: external_exports.record(
    external_exports.object({
      id: idSchema,
      speciesId: idSchema,
      version: external_exports.number().int().positive(),
      referencePhoto: legacyPhoto,
      representation: external_exports.string().min(1).max(200),
      imageUrl: external_exports.string(),
      sha256: external_exports.string().regex(/^[a-f0-9]{64}$/),
      reviewedAt: timestampSchema,
      method: external_exports.literal("reviewed-upload")
    }).strict()
  ),
  preferences: external_exports.object({
    palette: external_exports.enum(["twilight", "fieldnotes", "moonlit"]),
    reducedMotion: external_exports.boolean()
  }).strict()
}).strict();
function migrateV1(input, now = (/* @__PURE__ */ new Date()).toISOString()) {
  timestampSchema.parse(now);
  const legacy2 = legacySchema.parse(input);
  for (const [key, species] of Object.entries(legacy2.species))
    if (key !== species.id) throw new YardValidationError("legacySpeciesIdentity");
  for (const [key, art] of Object.entries(legacy2.artworks))
    if (key !== art.id || art.referencePhoto.speciesId !== art.speciesId)
      throw new YardValidationError("legacyArtworkIdentity");
  const stripSpecies = (species) => species;
  return yardDataSchema.parse({
    version: 2,
    species: Object.values(legacy2.species).map(stripSpecies),
    events: legacy2.identifications.map((event) => ({
      schemaVersion: 2,
      id: event.id,
      species: stripSpecies(event.species),
      observedAt: event.observedAt,
      ingestedAt: now,
      source: {
        kind: event.source.kind === "demo" ? "fixture" : event.source.kind === "manual" ? "manual" : "external",
        label: event.source.label,
        provider: "legacy-v1",
        sourceEventId: event.id
      },
      ...event.confidence === void 0 ? {} : { confidence: event.confidence },
      metadata: {
        legacySourceKind: event.source.kind,
        ...event.recordingUrl ? { legacyRecordingUrl: event.recordingUrl } : {},
        ...event.species.referencePhoto ? { referencePhoto: event.species.referencePhoto } : {}
      }
    })),
    collection: legacy2.residents.map((bird) => ({
      id: bird.id,
      speciesId: bird.speciesId,
      collectedAt: bird.savedAt
    })),
    birds: legacy2.residents.map((bird) => ({
      id: bird.id,
      speciesId: bird.speciesId,
      name: null,
      lifecycle: "permanent",
      createdAt: bird.savedAt,
      promotedAt: bird.savedAt,
      expiresAt: null,
      artworkId: bird.artworkId,
      originEventId: null
    })),
    artworks: Object.values(legacy2.artworks).map(
      (art) => artworkSchema.parse({
        id: art.id,
        speciesId: art.speciesId,
        version: art.version,
        status: "reviewed",
        imageUrl: art.imageUrl,
        sha256: art.sha256,
        representation: art.representation,
        provenance: {
          referencePhoto: art.referencePhoto,
          reviewedAt: art.reviewedAt,
          method: art.method,
          migratedFrom: 1
        }
      })
    ),
    preferences: { ...defaultPreferences(), ...legacy2.preferences }
  });
}

// src/lib/server/storage/repository.ts
var YardError = class extends Error {
  constructor(code, message) {
    super(message);
    this.code = code;
    this.name = "YardError";
  }
  code;
};
var nowIso = () => (/* @__PURE__ */ new Date()).toISOString();
var normalizeNow = (now) => new Date(timestampSchema.parse(now)).toISOString();
var checkOwner = (ownerId) => idSchema.parse(ownerId);
var clone = (value) => structuredClone(value);
var storedYardRowSchema = external_exports.object({
  schema_version: external_exports.number().int().positive().safe(),
  data: external_exports.string()
});
var YardRepository = class {
  constructor(pathOrDatabase, hooks = {}) {
    this.hooks = hooks;
    this.ownsDatabase = typeof pathOrDatabase === "string";
    if (typeof pathOrDatabase === "string") {
      if (pathOrDatabase !== ":memory:") mkdirSync(dirname(pathOrDatabase), { recursive: true });
      this.database = new DatabaseSync(pathOrDatabase);
      this.database.exec("PRAGMA journal_mode = WAL; PRAGMA busy_timeout = 5000;");
    } else this.database = pathOrDatabase;
    this.database.exec(
      "CREATE TABLE IF NOT EXISTS yard_migrations (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)"
    );
    const version2 = external_exports.object({ version: external_exports.number().int().positive().safe().nullable() }).parse(this.database.prepare("SELECT MAX(version) AS version FROM yard_migrations").get()).version ?? 0;
    if (version2 > 1)
      throw new YardError(
        "SCHEMA_VERSION",
        "Database is newer than this application; downgrade refused."
      );
    if (version2 < 1)
      this.transaction(() => {
        this.database.exec(
          "CREATE TABLE IF NOT EXISTS yard_owners (owner_id TEXT PRIMARY KEY NOT NULL, schema_version INTEGER NOT NULL, data TEXT NOT NULL CHECK(json_valid(data)))"
        );
        this.database.prepare("INSERT OR IGNORE INTO yard_migrations (version, applied_at) VALUES (1, ?)").run(nowIso());
      });
  }
  hooks;
  database;
  ownsDatabase;
  savepointSequence = 0;
  close() {
    if (this.ownsDatabase) this.database.close();
  }
  transaction(action) {
    if (this.database.isTransaction) {
      const name2 = `yard_operation_${++this.savepointSequence}`;
      this.database.exec(`SAVEPOINT ${name2}`);
      try {
        const result = action();
        this.database.exec(`RELEASE SAVEPOINT ${name2}`);
        return result;
      } catch (error) {
        this.database.exec(`ROLLBACK TO SAVEPOINT ${name2}`);
        this.database.exec(`RELEASE SAVEPOINT ${name2}`);
        throw error;
      }
    }
    this.database.exec("BEGIN IMMEDIATE");
    try {
      const result = action();
      this.database.exec("COMMIT");
      return result;
    } catch (error) {
      this.database.exec("ROLLBACK");
      throw error;
    }
  }
  read(ownerId) {
    checkOwner(ownerId);
    const value = this.database.prepare("SELECT schema_version, data FROM yard_owners WHERE owner_id = ?").get(ownerId);
    if (!value) return emptyYard();
    const row = storedYardRowSchema.safeParse(value);
    if (!row.success) throw new Error("Stored yard row is invalid.");
    if (row.data.schema_version !== 2)
      throw new YardError(
        "SCHEMA_VERSION",
        "Unsupported stored yard version; explicit migration required."
      );
    try {
      const data = JSON.parse(row.data.data);
      return yardDataSchema.parse(data);
    } catch {
      throw new Error("Stored yard data is invalid.");
    }
  }
  write(ownerId, state) {
    const validated = yardDataSchema.parse(state);
    const serialized = JSON.stringify(validated);
    if (Buffer.byteLength(serialized) > 16 * 1024 * 1024)
      throw new YardError(
        "INVALID",
        "Development yard limit reached; export before importing more."
      );
    this.database.prepare(
      "INSERT INTO yard_owners (owner_id, schema_version, data) VALUES (?, 2, ?) ON CONFLICT(owner_id) DO UPDATE SET schema_version = 2, data = excluded.data"
    ).run(checkOwner(ownerId), serialized);
  }
  mutate(ownerId, action, afterWrite) {
    checkOwner(ownerId);
    return this.transaction(() => {
      const state = this.read(ownerId);
      const result = action(state);
      this.write(ownerId, state);
      this.hooks.changed?.(ownerId, state);
      afterWrite?.(result);
      return result;
    });
  }
  snapshot(ownerId, now = nowIso()) {
    return snapshotOf(this.read(ownerId), normalizeNow(now));
  }
  importEvents(ownerId, input, now = nowIso()) {
    const serverNow = normalizeNow(now);
    const batch = Array.isArray(input) ? input : [input];
    if (batch.length > 1e3)
      throw new YardError("INVALID", "Import at most 1000 events per batch.");
    const incoming = batch.map((item) => importEventSchema.parse(item));
    return this.mutate(ownerId, (state) => this.insertEvents(ownerId, state, incoming, serverNow));
  }
  insertEvents(ownerId, state, incoming, serverNow) {
    let inserted = 0;
    let duplicates = 0;
    for (const raw2 of incoming) {
      const event = { ...raw2, ingestedAt: serverNow };
      const existing = state.events.find(
        (item) => item.id === event.id || sourceEventKey(item) === sourceEventKey(event)
      );
      if (existing) {
        if (evidenceFingerprint(existing) !== evidenceFingerprint(event))
          throw new YardError(
            "CONFLICT",
            "An event identity already has different evidence. The whole batch was kept unchanged."
          );
        duplicates++;
        continue;
      }
      const species = state.species.find((item) => item.id === event.species.id);
      if (species && species.scientificName !== event.species.scientificName)
        throw new YardError("CONFLICT", "Species identity conflicts with the existing taxon.");
      if (state.species.some(
        (item) => item.id !== event.species.id && item.scientificName.toLowerCase() === event.species.scientificName.toLowerCase()
      ))
        throw new YardError(
          "CONFLICT",
          "This taxon already has a different ID; resolve taxonomy before importing."
        );
      if (!species) state.species.push(clone(event.species));
      state.events.push(clone(event));
      inserted++;
      this.visit(ownerId, state, event, serverNow);
    }
    return { inserted, duplicates, snapshot: snapshotOf(state, serverNow) };
  }
  knownSpecies(state, speciesId) {
    const species = availableSpecies(state).find((entry) => entry.id === speciesId);
    if (!species) throw new YardError("INVALID", "Select a species from the available catalog.");
    return species;
  }
  addManualFinding(ownerId, input, now = nowIso()) {
    now = normalizeNow(now);
    const finding = manualFindingSchema.parse(input);
    return this.mutate(
      ownerId,
      (state) => {
        const id6 = `manual:${finding.id}`;
        return this.insertEvents(
          ownerId,
          state,
          [
            {
              schemaVersion: 2,
              id: id6,
              species: this.knownSpecies(state, finding.speciesId),
              observedAt: finding.observedAt === null ? null : new Date(finding.observedAt).toISOString(),
              source: { kind: "manual", label: "Manual entry", sourceEventId: id6 },
              metadata: { manualEntryVersion: 1, note: finding.note }
            }
          ],
          now
        );
      },
      (result) => {
        if (result.inserted === 1)
          this.hooks.manualInserted?.(ownerId, `manual:${finding.id}`, now);
      }
    );
  }
  /** Appends only; a retry checks its immutable receipt before checking the current revision. */
  correctEvents(ownerId, input, now = nowIso()) {
    now = normalizeNow(now);
    const incoming = correctionInputSchema.array().min(1).max(100).parse(input);
    return this.mutate(ownerId, (state) => {
      let inserted = 0, duplicates = 0;
      for (const correction of incoming) {
        const existing = state.corrections.find((entry) => entry.id === correction.id);
        if (existing) {
          if (canonicalJson({ ...existing, recordedAt: void 0 }) !== canonicalJson(correction))
            throw new YardError(
              "EVIDENCE_CONFLICT",
              "This correction submission already contains different changes. Review the latest history."
            );
          duplicates++;
          continue;
        }
        const current = effectiveEvidenceOf(state).find(
          (entry) => entry.eventId === correction.eventId
        );
        if (!current) throw new YardError("NOT_FOUND", "Observation not found in this yard.");
        if (!sameRevision(current, correction.expected))
          throw new YardError(
            "EVIDENCE_CONFLICT",
            "This observation changed since your draft. Review the latest correction before saving."
          );
        if (sameValue(current, correction.replacement))
          throw new YardError(
            "INVALID",
            "Change the species or observation time before saving a correction."
          );
        const species = this.knownSpecies(state, correction.replacement.speciesId);
        if (!state.species.some((entry) => entry.id === species.id)) state.species.push(species);
        state.corrections.push({ ...correction, recordedAt: now });
        inserted++;
      }
      return { inserted, duplicates, snapshot: snapshotOf(state, now) };
    });
  }
  selectableArtwork(ownerId, artwork, state) {
    return this.hooks.artworkSelectable?.(
      ownerId,
      artwork,
      state.species.find((species) => species.id === artwork.speciesId)
    ) ?? true;
  }
  visit(ownerId, state, event, now) {
    if (!event.observedAt) return;
    const observed = Date.parse(event.observedAt);
    const current = Date.parse(now);
    const expires = observed + state.preferences.visitorTtlHours * 36e5;
    if (observed > current || expires <= current) return;
    const active = state.birds.find(
      (bird) => bird.speciesId === event.species.id && (bird.lifecycle === "permanent" || bird.lifecycle === "temporary" && Date.parse(bird.expiresAt) > current)
    );
    if (active) {
      if (active.lifecycle === "temporary" && Date.parse(active.expiresAt) < expires)
        active.expiresAt = new Date(expires).toISOString();
      return;
    }
    const artwork = state.artworks.filter(
      (art) => art.speciesId === event.species.id && this.selectableArtwork(ownerId, art, state)
    ).sort((a, b) => b.version - a.version)[0];
    state.birds.push({
      id: randomUUID(),
      speciesId: event.species.id,
      name: null,
      lifecycle: "temporary",
      createdAt: now,
      expiresAt: new Date(expires).toISOString(),
      promotedAt: null,
      artworkId: artwork?.id ?? null,
      originEventId: event.id
    });
  }
  bird(state, birdId) {
    idSchema.parse(birdId);
    const bird = state.birds.find((item) => item.id === birdId);
    if (!bird) throw new YardError("NOT_FOUND", "Bird not found in this yard.");
    return bird;
  }
  collect(state, speciesId, now) {
    idSchema.parse(speciesId);
    if (!state.species.some((s) => s.id === speciesId))
      throw new YardError("NOT_FOUND", "Species not found in this collection.");
    if (!state.collection.some((entry) => entry.speciesId === speciesId))
      state.collection.push({ id: randomUUID(), speciesId, collectedAt: now });
  }
  promote(ownerId, birdId, name2, now = nowIso()) {
    now = normalizeNow(now);
    return this.mutate(ownerId, (state) => {
      const bird = this.bird(state, birdId);
      if (name2 !== void 0) bird.name = this.validName(name2);
      bird.lifecycle = "permanent";
      bird.expiresAt = null;
      bird.promotedAt ??= now;
      this.collect(state, bird.speciesId, now);
      return snapshotOf(state, now);
    });
  }
  validName(name2) {
    const trimmed = name2.trim();
    if (trimmed.length > 60 || hasControlCharacters(trimmed))
      throw new YardError(
        "INVALID",
        "Choose a name of at most 60 characters without control characters."
      );
    return trimmed || null;
  }
  rename(ownerId, birdId, name2, now = nowIso()) {
    now = normalizeNow(now);
    return this.mutate(ownerId, (state) => {
      this.bird(state, birdId).name = this.validName(name2);
      return snapshotOf(state, now);
    });
  }
  /** Remove only this display instance; evidence, species collection and immutable assets survive. */
  removeBird(ownerId, birdId, now = nowIso()) {
    now = normalizeNow(now);
    return this.mutate(ownerId, (state) => {
      this.bird(state, birdId);
      state.birds = state.birds.filter((bird) => bird.id !== birdId);
      return snapshotOf(state, now);
    });
  }
  addInstance(ownerId, speciesId, name2, now = nowIso()) {
    now = normalizeNow(now);
    return this.mutate(ownerId, (state) => {
      this.collect(state, speciesId, now);
      const artwork = state.artworks.filter((art) => art.speciesId === speciesId && this.selectableArtwork(ownerId, art, state)).sort((a, b) => b.version - a.version)[0];
      state.birds.push({
        id: randomUUID(),
        speciesId,
        name: name2 === void 0 ? null : this.validName(name2),
        lifecycle: "permanent",
        createdAt: now,
        promotedAt: now,
        expiresAt: null,
        artworkId: artwork?.id ?? null,
        originEventId: null
      });
      return snapshotOf(state, now);
    });
  }
  collectSpecies(ownerId, speciesId, now = nowIso()) {
    now = normalizeNow(now);
    return this.mutate(ownerId, (state) => {
      this.collect(state, speciesId, now);
      return snapshotOf(state, now);
    });
  }
  updatePreferences(ownerId, patch, now = nowIso()) {
    now = normalizeNow(now);
    const parsed = preferencesPatchSchema.parse(patch);
    return this.mutate(ownerId, (state) => {
      const next = preferencesSchema.parse({
        ...state.preferences,
        ...Object.fromEntries(Object.entries(parsed).filter(([, value]) => value !== void 0))
      });
      if (parsed.scene !== void 0 && parsed.scenePin === void 0)
        next.scenePin = legacyScenePin(next.scene);
      if (parsed.scene !== void 0 || parsed.scenePin !== void 0) {
        const resolved = resolveScene(next.scene, next.scenePin);
        if (resolved.status !== "ready")
          throw new YardError(
            "INVALID",
            "Select an available scene manifest. The saved yard was kept unchanged."
          );
        state.environment.objects = reanchorObjects(state.environment.objects, resolved.manifest);
      }
      state.preferences = next;
      return snapshotOf(state, now);
    });
  }
  addObject(ownerId, kind, now = nowIso()) {
    now = normalizeNow(now);
    objectKindSchema.parse(kind);
    return this.mutate(ownerId, (state) => {
      if (state.environment.objects.length >= MAX_OBJECTS)
        throw new YardError("INVALID", "A yard supports at most 12 objects.");
      if (availableStock(state.environment.inventory, state.environment.objects, kind) <= 0)
        throw new YardError(
          "INVALID",
          "No owned fixtures of this kind are available. Return one to inventory first."
        );
      const position = findObjectPlacement(
        kind,
        state.environment.objects,
        resolveScene(state.preferences.scene, state.preferences.scenePin).manifest
      );
      if (!position)
        throw new YardError(
          "INVALID",
          "There is no free space for this object. Move or remove another object first."
        );
      state.environment.objects.push({ id: randomUUID(), kind, ...position });
      return snapshotOf(state, now);
    });
  }
  moveObject(ownerId, objectId, x, y, now = nowIso(), expected) {
    now = normalizeNow(now);
    idSchema.parse(objectId);
    const baseline = expected ? placementSnapshotSchema.parse(expected) : void 0;
    return this.mutate(ownerId, (state) => {
      if (baseline && placementKey(baseline.scene, baseline.objects, baseline.scenePin) !== placementKey(
        state.preferences.scene,
        state.environment.objects,
        state.preferences.scenePin
      ))
        throw new YardError(
          "STALE_PLACEMENT",
          "The yard changed while you were arranging. Start the move again."
        );
      const object = state.environment.objects.find((item) => item.id === objectId);
      if (!object) throw new YardError("NOT_FOUND", "Object not found in this yard.");
      const moved = yardObjectSchema.parse({ ...object, x, y });
      const objects = state.environment.objects.map(
        (item) => item.id === objectId ? moved : item
      );
      state.environment.objects = validateObjects(
        objects,
        resolveScene(state.preferences.scene, state.preferences.scenePin).manifest
      );
      return snapshotOf(state, now);
    });
  }
  removeObject(ownerId, objectId, now = nowIso()) {
    now = normalizeNow(now);
    idSchema.parse(objectId);
    return this.mutate(ownerId, (state) => {
      if (!state.environment.objects.some((item) => item.id === objectId))
        throw new YardError("NOT_FOUND", "Object not found in this yard.");
      state.environment.objects = state.environment.objects.filter((item) => item.id !== objectId);
      return snapshotOf(state, now);
    });
  }
  /** Exact retries retain their receipt even after later moves, returns or restores. */
  objectInventory(ownerId, input, now = nowIso()) {
    now = normalizeNow(now);
    const command = objectInventoryCommandSchema.parse(input);
    const commandDigest = createHash("sha256").update(canonicalJson(command)).digest("hex");
    return this.mutate(ownerId, (state) => {
      const existing = state.environment.objectReceipts.find(
        (receipt) => receipt.requestId === command.requestId
      );
      if (existing) {
        if (existing.commandDigest !== commandDigest)
          throw new YardError(
            "CONFLICT",
            "This object request ID already belongs to a different operation."
          );
        return snapshotOf(state, now);
      }
      if (state.environment.objectReceipts.length >= MAX_OBJECT_OPERATION_RECEIPTS)
        throw new YardError(
          "INVALID",
          "The saved object-operation history is full. Existing retries still work; new operations require a future history upgrade."
        );
      const expected = command.expected;
      if (placementKey(expected.scene, expected.objects, expected.scenePin) !== placementKey(state.preferences.scene, state.environment.objects, state.preferences.scenePin))
        throw new YardError(
          "STALE_PLACEMENT",
          "The yard changed while you were arranging. Review the latest layout and start again."
        );
      const payload = command.payload;
      let resultObjectId;
      if (payload.operation === "place") {
        if (state.environment.objects.length >= MAX_OBJECTS)
          throw new YardError("INVALID", "A yard supports at most 12 objects.");
        if (availableStock(state.environment.inventory, state.environment.objects, payload.kind) <= 0)
          throw new YardError(
            "INVALID",
            "No owned fixtures of this kind are available. Return one to inventory first."
          );
        const position = findObjectPlacement(
          payload.kind,
          state.environment.objects,
          resolveScene(state.preferences.scene, state.preferences.scenePin).manifest
        );
        if (!position)
          throw new YardError(
            "INVALID",
            "There is no free space for this object. Move or return another object first."
          );
        resultObjectId = randomUUID();
        state.environment.objects.push({ id: resultObjectId, kind: payload.kind, ...position });
      } else {
        const object = state.environment.objects.find((item) => item.id === payload.objectId);
        if (!object) throw new YardError("NOT_FOUND", "Object not found in this yard.");
        resultObjectId = object.id;
        if (payload.operation === "return")
          state.environment.objects = state.environment.objects.filter(
            (item) => item.id !== object.id
          );
        else {
          const moved = yardObjectSchema.parse({ ...object, x: payload.x, y: payload.y });
          state.environment.objects = validateObjects(
            state.environment.objects.map((item) => item.id === object.id ? moved : item),
            resolveScene(state.preferences.scene, state.preferences.scenePin).manifest
          );
        }
      }
      state.environment.objectReceipts.push({
        requestId: command.requestId,
        commandDigest,
        resultObjectId
      });
      return snapshotOf(state, now);
    });
  }
  updateWeather(ownerId, settings, now = nowIso()) {
    now = normalizeNow(now);
    const parsed = weatherSettingsSchema.parse(settings);
    return this.mutate(ownerId, (state) => {
      state.environment.weather = parsed;
      return snapshotOf(state, now);
    });
  }
  registerArtwork(ownerId, input, now = nowIso()) {
    now = normalizeNow(now);
    const art = artworkSchema.parse(input);
    return this.mutate(ownerId, (state) => {
      if (!state.species.some((s) => s.id === art.speciesId))
        throw new YardError("NOT_FOUND", "Artwork requires a known species.");
      if (state.artworks.some(
        (a) => a.id === art.id || a.speciesId === art.speciesId && a.version === art.version
      ))
        throw new YardError("CONFLICT", "Artwork is immutable; create a new ID and version.");
      state.artworks.push(art);
      for (const bird of state.birds)
        if (bird.speciesId === art.speciesId && !bird.artworkId && this.selectableArtwork(ownerId, art, state))
          bird.artworkId = art.id;
      return snapshotOf(state, now);
    });
  }
  /** Explicit per-resident selection; never auto-pins siblings or mutates previous art. */
  pinAnimation(ownerId, birdId, input, now = nowIso()) {
    now = normalizeNow(now);
    return this.mutate(ownerId, (state) => {
      const bird = this.bird(state, birdId);
      if (bird.speciesId !== input.speciesId)
        throw new YardError("INVALID", "Animation species does not match this bird.");
      const art = artworkSchema.parse({
        ...input,
        id: randomUUID(),
        version: 1 + Math.max(
          0,
          ...state.artworks.filter((a) => a.speciesId === bird.speciesId).map((a) => a.version)
        )
      });
      if (!art.animationPin) throw new YardError("INVALID", "An exact animation pin is required.");
      if (!this.selectableArtwork(ownerId, art, state))
        throw new YardError(
          "CONFLICT",
          "Restore this archived or unavailable asset dependency before selecting it."
        );
      const existing = state.artworks.find(
        (a) => a.speciesId === art.speciesId && JSON.stringify(a.animationPin) === JSON.stringify(art.animationPin)
      );
      if (!existing) state.artworks.push(art);
      bird.artworkId = existing?.id ?? art.id;
      return snapshotOf(state, now);
    });
  }
  /** Lifecycle CAS; immutable artwork and evidence remain available for explicit undo. */
  pinCatalog(ownerId, birdId, expectedArtworkId, input, now = nowIso()) {
    now = normalizeNow(now);
    return this.mutate(ownerId, (state) => {
      const bird = this.bird(state, birdId);
      if (bird.artworkId !== expectedArtworkId)
        throw new YardError(
          "CONFLICT",
          "This bird\u2019s artwork changed. Refresh before selecting a catalog version."
        );
      if (bird.speciesId !== input.speciesId)
        throw new YardError("INVALID", "Catalog species does not match this bird.");
      const art = artworkSchema.parse({
        ...input,
        id: randomUUID(),
        version: 1 + Math.max(
          0,
          ...state.artworks.filter((a) => a.speciesId === bird.speciesId).map((a) => a.version)
        )
      });
      if (!art.catalogPin || !this.selectableArtwork(ownerId, art, state))
        throw new YardError(
          "CONFLICT",
          "This shared catalog release is unavailable for selection."
        );
      const existing = state.artworks.find(
        (a) => a.speciesId === art.speciesId && a.catalogPin && canonicalJson(a.catalogPin) === canonicalJson(art.catalogPin) && this.selectableArtwork(ownerId, a, state)
      );
      if (!existing) state.artworks.push(art);
      bird.artworkId = existing?.id ?? art.id;
      return snapshotOf(state, now);
    });
  }
  /** Lifecycle CAS; immutable artwork and evidence remain available for explicit undo. */
  replaceArtworkSelection(ownerId, birdId, expected, next, now = nowIso()) {
    return this.mutate(ownerId, (state) => {
      const bird = this.bird(state, birdId);
      if (bird.artworkId !== expected)
        throw new YardError(
          "CONFLICT",
          "This bird\u2019s artwork changed. Refresh before trying again."
        );
      if (next !== null) {
        const art = state.artworks.find(
          (item) => item.id === next && item.speciesId === bird.speciesId
        );
        if (!art || !this.selectableArtwork(ownerId, art, state))
          throw new YardError(
            "CONFLICT",
            "Restore the archived or unavailable asset dependency before restoring this pin."
          );
      }
      bird.artworkId = next;
      return snapshotOf(state, normalizeNow(now));
    });
  }
  exportBackup(ownerId, now = nowIso()) {
    return backupSchema.parse({
      format: "chirpneighbors-yard",
      version: 2,
      exportedAt: normalizeNow(now),
      data: this.read(ownerId)
    });
  }
  /** Explicit replacement of this owner's yard; supplied owner IDs are never accepted. */
  restoreBackup(ownerId, input, now = nowIso()) {
    now = normalizeNow(now);
    checkOwner(ownerId);
    const data = external_exports.object({ version: external_exports.literal(1) }).safeParse(input).success ? migrateV1(input, now) : backupSchema.parse(input).data;
    return this.transaction(() => {
      const current = this.read(ownerId);
      for (const bird of data.birds) {
        if (bird.artworkId === null) continue;
        const art = data.artworks.find((item) => item.id === bird.artworkId);
        const priorBird = current.birds.find((item) => item.id === bird.id);
        const priorArt = current.artworks.find((item) => item.id === priorBird?.artworkId);
        if (art && (priorBird?.artworkId !== bird.artworkId || canonicalJson(priorArt ?? null) !== canonicalJson(art)) && !this.selectableArtwork(ownerId, art, data))
          throw new YardError(
            "CONFLICT",
            "This backup would newly select an archived or unavailable asset. Restore the asset first."
          );
      }
      const receipts = new Map(
        this.read(ownerId).environment.objectReceipts.map((receipt) => [
          receipt.requestId,
          receipt
        ])
      );
      for (const receipt of data.environment.objectReceipts) {
        const existing = receipts.get(receipt.requestId);
        if (existing && canonicalJson(existing) !== canonicalJson(receipt))
          throw new YardError(
            "CONFLICT",
            "The backup conflicts with a saved object-operation receipt."
          );
        receipts.set(receipt.requestId, receipt);
      }
      if (receipts.size > MAX_OBJECT_OPERATION_RECEIPTS)
        throw new YardError(
          "INVALID",
          "The combined object-operation history exceeds this version\u2019s capacity."
        );
      data.environment.objectReceipts = [...receipts.values()];
      this.write(ownerId, data);
      this.hooks.changed?.(ownerId, data);
      this.hooks.restored?.(ownerId, now);
      return snapshotOf(data, now);
    });
  }
  migrateV1(ownerId, input, now = nowIso()) {
    return this.restoreBackup(ownerId, input, now);
  }
};

// src/lib/auth/session-binding.ts
var SESSION_CHANGED_MESSAGE = "Your sign-in session changed. Reload this page before continuing.";
var sessionBindingSchema = external_exports.string().regex(/^[A-Za-z0-9_-]{43}$/);
var sessionContextSchema = external_exports.object({ sessionBinding: sessionBindingSchema.nullable() }).strict();
var sessionChangedSchema = external_exports.object({
  version: external_exports.literal(1),
  kind: external_exports.literal("auth.session-changed"),
  code: external_exports.literal("session_changed"),
  error: external_exports.literal(SESSION_CHANGED_MESSAGE)
}).strict();

// src/lib/domain/commands.ts
var name = external_exports.string().max(60);
var moveObjectCommandSchema = external_exports.object({
  action: external_exports.literal("move-object"),
  objectId: idSchema,
  x: external_exports.number().finite(),
  y: external_exports.number().finite(),
  expected: placementSnapshotSchema.optional()
}).strict();
var placementCommandSchema = moveObjectCommandSchema.extend({ expected: placementSnapshotSchema }).strict();
var yardCommandSchema = external_exports.discriminatedUnion("action", [
  objectInventoryCommandSchema,
  ...findingCommandSchema.options,
  external_exports.object({ action: external_exports.literal("fixtures") }).strict(),
  external_exports.object({
    action: external_exports.literal("pin-animation"),
    birdId: idSchema,
    jobId: idSchema,
    artifactId: idSchema
  }).strict(),
  external_exports.object({ action: external_exports.literal("add-object"), kind: objectKindSchema }).strict(),
  moveObjectCommandSchema,
  external_exports.object({ action: external_exports.literal("remove-object"), objectId: idSchema }).strict(),
  external_exports.object({ action: external_exports.literal("weather"), weather: weatherSettingsSchema }).strict(),
  external_exports.object({ action: external_exports.literal("import"), events: external_exports.unknown() }).strict(),
  external_exports.object({ action: external_exports.literal("promote"), birdId: idSchema, name: name.optional() }).strict(),
  external_exports.object({ action: external_exports.literal("rename"), birdId: idSchema, name }).strict(),
  external_exports.object({ action: external_exports.literal("add-instance"), speciesId: idSchema, name: name.optional() }).strict(),
  external_exports.object({ action: external_exports.literal("collect"), speciesId: idSchema }).strict(),
  external_exports.object({ action: external_exports.literal("remove"), birdId: idSchema }).strict(),
  external_exports.object({ action: external_exports.literal("preferences"), preferences: preferencesPatchSchema }).strict(),
  external_exports.object({ action: external_exports.literal("restore"), backup: external_exports.unknown(), confirmed: external_exports.literal(true) }).strict()
]);

// src/lib/assets/intake.ts
var identifier2 = external_exports.string().min(1).max(160).regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]*$/);
var hash = external_exports.string().regex(/^[a-f0-9]{64}$/);
var label = external_exports.string().trim().min(1).max(200);
var manifestShape = speciesManifestV2Schema.innerType().shape;
var assetSourceSchema = external_exports.object({
  schemaVersion: external_exports.literal(1),
  speciesId: identifier2,
  representation: label,
  source: external_exports.enum(["deterministic_fixture", "user_upload", "provider"]),
  creator: identifier2,
  sourceVersion: identifier2,
  license: external_exports.object({
    id: label,
    status: external_exports.enum(["development-only", "cleared", "pending", "denied"]),
    derivativesAllowed: external_exports.boolean(),
    redistributionAllowed: external_exports.boolean(),
    evidenceId: identifier2.nullable(),
    attribution: external_exports.string().trim().min(1).max(300)
  }).strict(),
  references: external_exports.array(
    external_exports.object({
      id: identifier2,
      speciesId: identifier2,
      contentDigest: hash,
      role: external_exports.enum(["technical-fixture", "species-reference"])
    }).strict()
  ).min(1).max(16),
  fidelityReview: external_exports.object({
    reviewerId: identifier2,
    reviewedAt: external_exports.string().datetime(),
    evidenceId: identifier2
  }).strict().nullable()
}).strict();
var pixelAnimationSourceSchema = external_exports.object({
  schemaVersion: external_exports.literal(1),
  format: external_exports.literal("rgba8-frames"),
  canvas: manifestShape.canvas,
  logicalPixelSize: external_exports.number().int().min(1).max(16),
  paletteLimit: external_exports.number().int().min(1).max(64),
  frames: external_exports.array(
    external_exports.object({
      rgba: external_exports.array(external_exports.number().int().min(0).max(255)).min(4).max(256 * 256 * 4)
    }).strict()
  ).min(1).max(64),
  clips: manifestShape.clips
}).strict();
var assetPackagingInputSchema = external_exports.object({
  schemaVersion: external_exports.literal(1),
  source: assetSourceSchema,
  pixels: pixelAnimationSourceSchema
}).strict();
var assetGenerationInputSchema = external_exports.object({
  schemaVersion: external_exports.literal(1),
  source: assetSourceSchema,
  requestedStates: external_exports.array(external_exports.enum(animationStates)).min(1).max(9)
}).strict();

// src/lib/assets/metrics-v3.ts
function measureLoopEdges(canvas, frames, clips) {
  const cache = /* @__PURE__ */ new Map();
  function pixels(index) {
    const cached = cache.get(index);
    if (cached) return cached;
    const frame = frames[index];
    if (!frame) throw new Error("Loop metric references an absent frame.");
    const output = new Uint32Array(canvas.width * canvas.height);
    for (const rect of frame)
      for (let y = rect.y; y < Math.min(canvas.height, rect.y + rect.height); y++)
        for (let x = rect.x; x < Math.min(canvas.width, rect.x + rect.width); x++)
          output[y * canvas.width + x] = rect.color + 1;
    cache.set(index, output);
    return output;
  }
  return animationStates.flatMap((action) => {
    const clip3 = clips[action];
    if (!clip3?.loop) return [];
    const first = clip3.poses[0], last = clip3.poses.at(-1);
    if (!first || !last) throw new Error("Loop metric requires a pose.");
    const left = pixels(first.frame), right = pixels(last.frame);
    let changedPixels = 0;
    for (let index = 0; index < left.length; index++)
      if (left[index] !== right[index]) changedPixels++;
    const contacts = (pose) => JSON.stringify(
      [...pose.contacts].sort((a, b) => a.kind < b.kind ? -1 : a.kind > b.kind ? 1 : 0)
    );
    return [
      {
        action,
        comparedPixels: left.length,
        changedPixels,
        pivotDistance: Math.hypot(first.pivot.x - last.pivot.x, first.pivot.y - last.pivot.y),
        contactLayoutChanged: contacts(first) !== contacts(last)
      }
    ];
  });
}

// src/lib/assets/shape.ts
var coordinate = external_exports.number().int().min(0).max(256);
var point2 = external_exports.object({ x: coordinate, y: coordinate }).strict();
var id = external_exports.string().min(1).max(160).regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]*$/);
var physicalFootprintSchema = external_exports.object({
  left: external_exports.number().int().min(0).max(128),
  right: external_exports.number().int().min(0).max(128),
  back: external_exports.number().int().min(0).max(64),
  front: external_exports.number().int().min(0).max(64)
}).strict().refine(
  (value) => value.left + value.right > 0 && value.back + value.front > 0,
  "Physical footprint must have positive width and depth."
);
var visualBoundsSchema = external_exports.object({
  x: coordinate,
  y: coordinate,
  width: external_exports.number().int().min(1).max(256),
  height: external_exports.number().int().min(1).max(256)
}).strict();
var shapePoseSchema = external_exports.object({
  poseId: id,
  frame: external_exports.number().int().min(0).max(63),
  visualBounds: visualBoundsSchema,
  support: point2,
  footprint: physicalFootprintSchema,
  landmarks: external_exports.array(
    point2.extend({ kind: external_exports.enum(["head", "body", "beak", "tail", "left-foot", "right-foot"]) }).strict()
  ).max(6)
}).strict();
var shapeReviewSchema = external_exports.object({
  schemaVersion: external_exports.literal(1),
  basedOn: animationPinSchema,
  speciesId: id,
  masterPoseId: id,
  poses: external_exports.array(shapePoseSchema).min(1).max(576)
}).strict().superRefine((value, context) => {
  if (new Set(value.poses.map((pose) => pose.poseId)).size !== value.poses.length)
    context.addIssue({ code: "custom", message: "Shape pose IDs must be unique." });
  if (!value.poses.some((pose) => pose.poseId === value.masterPoseId))
    context.addIssue({ code: "custom", message: "Master pose must identify an annotated pose." });
  if (value.poses.some(
    (pose) => new Set(pose.landmarks.map((point3) => point3.kind)).size !== pose.landmarks.length
  ))
    context.addIssue({ code: "custom", message: "Landmark kinds must be distinct per pose." });
});
function opaqueBounds(rectangles) {
  if (!rectangles.length) return null;
  const x = Math.min(...rectangles.map((rect) => rect.x));
  const y = Math.min(...rectangles.map((rect) => rect.y));
  return {
    x,
    y,
    width: Math.max(...rectangles.map((rect) => rect.x + rect.width)) - x,
    height: Math.max(...rectangles.map((rect) => rect.y + rect.height)) - y
  };
}
function shapeReviewIssues(manifest, shape2) {
  const issues = [];
  const poses = [
    ...new Map(
      Object.values(manifest.clips).flatMap((clip3) => clip3?.poses ?? []).map((pose) => [pose.poseId, pose])
    ).values()
  ];
  const occurrences = Object.values(manifest.clips).flatMap((clip3) => clip3?.poses ?? []);
  if (occurrences.some(
    (pose) => poses.some((unique) => unique.poseId === pose.poseId && unique.frame !== pose.frame)
  ))
    issues.push("Repeated pose identities must retain the same frame.");
  if (shape2.speciesId !== manifest.speciesId) issues.push("Shape species differs from its pixels.");
  if (poses.length !== shape2.poses.length || poses.some(
    (pose) => !shape2.poses.some((entry) => entry.poseId === pose.poseId && entry.frame === pose.frame)
  ))
    issues.push("Shape annotations must bind every exact authored pose and frame.");
  for (const pose of shape2.poses) {
    const bounds = opaqueBounds(manifest.frames[pose.frame] ?? []);
    if (!bounds || ["x", "y", "width", "height"].some((key) => bounds[key] !== pose.visualBounds[key]))
      issues.push(`Shape visual bounds do not match opaque frame: ${pose.poseId}.`);
    const points = [pose.support, ...pose.landmarks];
    if (points.some((point3) => point3.x > manifest.canvas.width || point3.y > manifest.canvas.height))
      issues.push(`Shape point exceeds canvas: ${pose.poseId}.`);
    if (bounds && (pose.support.x < bounds.x || pose.support.x > bounds.x + bounds.width || pose.support.y < bounds.y || pose.support.y > bounds.y + bounds.height))
      issues.push(`Support must lie within the opaque extent: ${pose.poseId}.`);
  }
  return issues;
}

// src/lib/assets/manifest-v3.ts
var legacy = speciesManifestV2Schema.innerType().shape;
var id2 = external_exports.string().min(1).max(160).regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]*$/);
var integer2 = external_exports.number().int().min(0).max(Number.MAX_SAFE_INTEGER);
var pointSchema = external_exports.object({ x: integer2.max(256), y: integer2.max(256) }).strict();
var contactSchema = pointSchema.extend({
  kind: external_exports.enum(["left-foot", "right-foot", "perch", "ground"])
}).strict();
var animationPoseSchema = external_exports.object({
  frame: integer2.max(63),
  durationTicks: external_exports.number().int().min(1).max(300),
  pivot: pointSchema,
  contacts: external_exports.array(contactSchema).max(4),
  poseId: id2,
  rotation: external_exports.number().min(-0.5).max(0.5)
}).strict();
var animationClipV3Schema = external_exports.object({
  action: external_exports.enum(animationStates),
  direction: external_exports.literal("right-facing-mirrorable"),
  loop: external_exports.boolean(),
  poses: external_exports.array(animationPoseSchema).min(1).max(256)
}).strict();
var animationClipsV3Schema = external_exports.object({
  idle: animationClipV3Schema,
  moving: animationClipV3Schema.optional(),
  perching: animationClipV3Schema.optional(),
  singing: animationClipV3Schema.optional(),
  feeding: animationClipV3Schema.optional(),
  bathing: animationClipV3Schema.optional(),
  sleeping: animationClipV3Schema.optional(),
  playing: animationClipV3Schema.optional(),
  nesting: animationClipV3Schema.optional()
}).strict();
var taxonomyIdentitySchema = external_exports.object({
  catalog: external_exports.literal("chirp-display-catalog"),
  version: external_exports.literal(1),
  speciesId: id2
}).strict().superRefine((value, context) => {
  if (!catalogEntry(value.speciesId))
    context.addIssue({
      code: "custom",
      message: "Species is absent from the pinned application catalog."
    });
});
var reviewedReferenceSchema = external_exports.object({
  id: id2,
  roles: external_exports.array(external_exports.enum(["species", "style", "pose"])).min(1).max(3),
  pin: animationPinSchema
}).strict().superRefine((value, context) => {
  if (new Set(value.roles).size !== value.roles.length)
    context.addIssue({ code: "custom", message: "Reference roles must be distinct." });
});
var poseGraphSchema = external_exports.object({
  nodes: external_exports.array(
    external_exports.object({
      id: id2,
      frame: integer2.max(63),
      action: external_exports.enum(animationStates),
      referenceId: id2
    }).strict()
  ).min(1).max(576),
  edges: external_exports.array(external_exports.object({ from: id2, to: id2 }).strict()).max(2304)
}).strict();
var animationConditioningSchema = external_exports.object({
  taxonomy: taxonomyIdentitySchema,
  references: external_exports.array(reviewedReferenceSchema).min(1).max(16),
  poseGraph: poseGraphSchema
}).strict();
var normalizationReportSchema = external_exports.object({
  algorithm: external_exports.literal("lossless-rgba-rects-v2"),
  alpha: external_exports.literal("binary"),
  logicalPixelSize: external_exports.number().int().min(1).max(16),
  palette: external_exports.array(external_exports.number().int().min(0).max(16777215)).min(1).max(64),
  loopEdges: external_exports.array(
    external_exports.object({
      action: external_exports.enum(animationStates),
      comparedPixels: integer2.min(1).max(65536),
      changedPixels: integer2.max(65536),
      pivotDistance: external_exports.number().min(0).max(512),
      contactLayoutChanged: external_exports.boolean()
    }).strict()
  ).max(9)
}).strict();
var metricGeometrySchema = external_exports.object({
  canvas: legacy.canvas.omit({ anchorX: true, anchorY: true }),
  frames: legacy.frames,
  clips: animationClipsV3Schema
}).strip();
var speciesManifestV3Schema = external_exports.object({
  schemaVersion: external_exports.literal(3),
  speciesId: legacy.speciesId,
  representation: legacy.representation,
  fixture: legacy.fixture,
  taxonFidelityReviewed: legacy.taxonFidelityReviewed,
  format: legacy.format,
  canvas: legacy.canvas.omit({ anchorX: true, anchorY: true }),
  frames: legacy.frames,
  clips: animationClipsV3Schema,
  provenance: legacy.provenance,
  conditioning: animationConditioningSchema,
  sourceArtifact: animationPinSchema,
  normalization: normalizationReportSchema,
  shape: shapeReviewSchema.optional()
}).strict().superRefine((value, context) => {
  const fail = (message) => context.addIssue({ code: "custom", message });
  const { width, height } = value.canvas;
  if (width * height * value.frames.length > 65536) {
    fail("Decoded animation exceeds pixel budget.");
    return;
  }
  if (value.frames.reduce((sum, frame) => sum + frame.length, 0) > 16384)
    fail("Manifest exceeds rectangle budget.");
  if (value.conditioning.taxonomy.speciesId !== value.speciesId)
    fail("Taxonomy and manifest species differ.");
  if (value.fixture ? value.taxonFidelityReviewed || value.provenance.source !== "deterministic_fixture" || value.provenance.usage !== "development-only" : !value.taxonFidelityReviewed || value.provenance.source === "deterministic_fixture" || value.provenance.usage !== "cleared")
    fail("Fixture/fidelity provenance is inconsistent.");
  const grid = value.normalization.logicalPixelSize;
  if (width % grid || height % grid) fail("Canvas does not align to logical grid.");
  const colors = /* @__PURE__ */ new Set();
  for (const frame of value.frames)
    for (const rect of frame) {
      if (rect.x + rect.width > width || rect.y + rect.height > height)
        fail("Frame exceeds canvas bounds.");
      if (rect.x % grid || rect.y % grid || rect.width % grid || rect.height % grid)
        fail("Rectangle does not align to logical grid.");
      colors.add(rect.color);
    }
  if (new Set(value.normalization.palette).size !== value.normalization.palette.length || value.normalization.palette.length !== colors.size || value.normalization.palette.some((color) => !colors.has(color)))
    fail("Palette does not match authored pixels.");
  const refs = value.conditioning.references;
  if (new Set(refs.map((ref) => ref.id)).size !== refs.length || refs.filter((ref) => ref.roles.includes("style")).length !== 1)
    fail("Conditioning requires unique references and exactly one reviewed style reference.");
  const graph = value.conditioning.poseGraph;
  const nodes = new Map(graph.nodes.map((node) => [node.id, node]));
  if (nodes.size !== graph.nodes.length) fail("Pose node IDs must be unique.");
  for (const node of graph.nodes)
    if (node.frame >= value.frames.length || !refs.some((ref) => ref.id === node.referenceId && ref.roles.includes("pose")))
      fail("Pose reference/frame is unavailable.");
  const edgeKey = (from, to) => JSON.stringify([from, to]);
  const declaredEdges = new Set(graph.edges.map((edge) => edgeKey(edge.from, edge.to)));
  if (declaredEdges.size !== graph.edges.length || graph.edges.some((edge) => !nodes.has(edge.from) || !nodes.has(edge.to)))
    fail("Pose edges must be unique and reference available nodes.");
  const usedNodes = /* @__PURE__ */ new Set(), usedEdges = /* @__PURE__ */ new Set();
  const loops = /* @__PURE__ */ new Set();
  for (const [action, clip3] of Object.entries(value.clips)) {
    if (!clip3) continue;
    if (clip3.action !== action) fail("Clip action must match its registered state.");
    for (const [index, pose] of clip3.poses.entries()) {
      const node = nodes.get(pose.poseId);
      if (!node || node.frame !== pose.frame || node.action !== action)
        fail("Clip pose does not match its graph node.");
      usedNodes.add(pose.poseId);
      if (pose.frame >= value.frames.length || pose.pivot.x > width || pose.pivot.y > height || pose.contacts.some((contact2) => contact2.x > width || contact2.y > height))
        fail("Clip frame/pivot/contact exceeds bounds.");
      if (new Set(pose.contacts.map((contact2) => contact2.kind)).size !== pose.contacts.length)
        fail("Contact kinds must be unique per pose.");
      const next = clip3.poses[index + 1] ?? (clip3.loop ? clip3.poses[0] : void 0);
      if (next) usedEdges.add(edgeKey(pose.poseId, next.poseId));
    }
    if (clip3.loop) loops.add(action);
  }
  if (usedNodes.size !== nodes.size || usedEdges.size !== declaredEdges.size || [...usedEdges].some((edge) => !declaredEdges.has(edge)))
    fail("Pose graph must describe exactly the authored clip transitions.");
  const metrics = value.normalization.loopEdges;
  if (new Set(metrics.map((entry) => entry.action)).size !== metrics.length || metrics.length !== loops.size || metrics.some(
    (entry) => !loops.has(entry.action) || entry.comparedPixels !== width * height || entry.changedPixels > entry.comparedPixels
  ))
    fail("Loop metrics do not match authored looping clips.");
  const validIndices = Object.values(value.clips).every(
    (clip3) => !clip3 || clip3.poses.every((pose) => pose.frame < value.frames.length)
  );
  if (validIndices && metricGeometrySchema.safeParse(value).success) {
    if (value.shape) for (const issue of shapeReviewIssues(value, value.shape)) fail(issue);
    const measured = measureLoopEdges(value.canvas, value.frames, value.clips);
    if (measured.some((entry) => {
      const declared = metrics.find((metric) => metric.action === entry.action);
      return !declared || declared.changedPixels !== entry.changedPixels || declared.pivotDistance !== entry.pivotDistance || declared.contactLayoutChanged !== entry.contactLayoutChanged;
    }))
      fail("Loop metrics do not match decoded frame edges.");
  }
});

// src/lib/assets/png-origin.ts
var PNG_MAX_BYTES = 524288;
var PNG_MAX_PIXELS = 65536;
var PNG_MAX_DIMENSION = 1024;
var hash2 = external_exports.string().regex(/^[a-f0-9]{64}$/);
var bytes = external_exports.number().int().min(1).max(PNG_MAX_BYTES);
var pngFileIdentitySchema = external_exports.object({
  schemaVersion: external_exports.literal(1),
  id: external_exports.string().uuid(),
  original: external_exports.object({ sha256: hash2, bytes }).strict(),
  canonical: external_exports.object({
    sha256: hash2,
    bytes,
    rgbaSha256: hash2,
    width: external_exports.number().int().min(1).max(PNG_MAX_DIMENSION),
    height: external_exports.number().int().min(1).max(PNG_MAX_DIMENSION)
  }).strict(),
  decoder: external_exports.object({
    id: external_exports.literal("sharp"),
    version: external_exports.string().min(1).max(40),
    libvips: external_exports.string().min(1).max(40)
  }).strict(),
  normalization: external_exports.literal("chirp-png-straight-srgb8-hidden-rgb-zero-v1")
}).strict().superRefine((value, context) => {
  if (value.canonical.width * value.canonical.height > PNG_MAX_PIXELS)
    context.addIssue({ code: "custom", message: "PNG pixel budget exceeded." });
});
var pngFrameLayoutSchema = external_exports.object({
  width: external_exports.number().int().min(1).max(256),
  height: external_exports.number().int().min(1).max(256),
  columns: external_exports.number().int().min(1).max(64),
  rows: external_exports.number().int().min(1).max(64)
}).strict().superRefine((value, context) => {
  if (value.columns * value.rows > 64 || value.width * value.height * value.columns * value.rows > PNG_MAX_PIXELS)
    context.addIssue({ code: "custom", message: "PNG frame budget exceeded." });
});
var pngFileOriginSchema = external_exports.object({
  file: pngFileIdentitySchema,
  reviewDigest: hash2,
  layout: pngFrameLayoutSchema
}).strict();

// src/lib/assets/intake-v2.ts
var id3 = external_exports.string().min(1).max(160).regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]*$/);
var hash3 = external_exports.string().regex(/^[a-f0-9]{64}$/);
var localModelManifestSchema = external_exports.object({
  id: id3,
  revision: id3,
  weightsSha256: hash3,
  license: external_exports.object({ id: id3, contentSha256: hash3 }).strict(),
  adapters: external_exports.array(
    external_exports.object({
      id: id3,
      revision: id3,
      weightsSha256: hash3,
      parentWeightsSha256: hash3,
      license: external_exports.object({ id: id3, contentSha256: hash3 }).strict()
    }).strict()
  ).max(8)
}).strict().superRefine((value, context) => {
  if (new Set(value.adapters.map((adapter) => adapter.id)).size !== value.adapters.length || value.adapters.some((adapter) => adapter.parentWeightsSha256 !== value.weightsSha256))
    context.addIssue({
      code: "custom",
      message: "Adapter IDs must be unique and pin the declared parent model weights."
    });
});
var unsupportedStrategy = external_exports.object({
  version: external_exports.literal(1),
  execution: external_exports.literal("unconfigured-local"),
  model: localModelManifestSchema,
  alphaPlan: external_exports.enum(["native-binary", "native-continuous", "layered", "matting-required"])
}).strict();
var generationStrategySchema = external_exports.discriminatedUnion("kind", [
  external_exports.object({
    kind: external_exports.literal("decoded-rgba"),
    version: external_exports.literal(1),
    alphaOrigin: external_exports.enum(["technical-fixture", "native", "upstream-cleanup", "unknown"]),
    output: external_exports.literal("rgba8-binary")
  }).strict(),
  unsupportedStrategy.extend({ kind: external_exports.literal("direct-spritesheet") }).strict(),
  unsupportedStrategy.extend({ kind: external_exports.literal("conditioned-frame-edit") }).strict(),
  unsupportedStrategy.extend({ kind: external_exports.literal("video-extract") }).strict(),
  unsupportedStrategy.extend({ kind: external_exports.literal("rigged-deterministic") }).strict()
]);
var pixelAnimationSourceV2Schema = pixelAnimationSourceSchema.omit({ clips: true }).extend({
  schemaVersion: external_exports.literal(2),
  canvas: speciesManifestV2Schema.innerType().shape.canvas.omit({ anchorX: true, anchorY: true })
}).strict();
var assetPackagingInputV2Schema = external_exports.object({
  schemaVersion: external_exports.literal(2),
  source: assetSourceSchema,
  pixels: pixelAnimationSourceV2Schema,
  clips: animationClipsV3Schema,
  conditioning: animationConditioningSchema,
  strategy: generationStrategySchema,
  shape: shapeReviewSchema.optional(),
  fileOrigin: pngFileOriginSchema.optional()
}).strict().superRefine((value, context) => {
  if (value.conditioning.taxonomy.speciesId !== value.source.speciesId)
    context.addIssue({ code: "custom", message: "Source and pinned taxonomy species differ." });
  if (value.strategy.kind === "decoded-rgba" && value.source.source === "deterministic_fixture" !== (value.strategy.alphaOrigin === "technical-fixture"))
    context.addIssue({
      code: "custom",
      message: "Technical fixture alpha declarations cannot claim native generation."
    });
  const refs = value.conditioning.references;
  if (new Set(refs.map((reference) => reference.id)).size !== refs.length || value.source.references.length !== refs.length || refs.some(
    (reference) => !value.source.references.some(
      (source) => source.id === reference.id && source.contentDigest === reference.pin.contentDigest
    )
  ))
    context.addIssue({
      code: "custom",
      message: "Conditioning pins must match every declared source reference and hash."
    });
});
var rgbaSourceArtifactSchema = external_exports.object({
  schemaVersion: external_exports.literal(1),
  format: external_exports.literal("private-rgba-source"),
  lifecycle: external_exports.literal("retained-until-owner-deletion"),
  inputDigest: hash3,
  input: assetPackagingInputV2Schema,
  blobs: external_exports.array(
    external_exports.object({
      frame: external_exports.number().int().min(0).max(63),
      encoding: external_exports.literal("rgba8"),
      bytes: external_exports.number().int().min(4).max(256 * 256 * 4),
      sha256: hash3
    }).strict()
  ).min(1).max(64)
}).strict().superRefine((value, context) => {
  if (value.blobs.length !== value.input.pixels.frames.length || value.blobs.some(
    (blob, index) => blob.frame !== index || blob.bytes !== value.input.pixels.canvas.width * value.input.pixels.canvas.height * 4 || blob.bytes !== value.input.pixels.frames[index]?.rgba.length
  ))
    context.addIssue({
      code: "custom",
      message: "Source blob descriptors must match every decoded frame."
    });
});

// src/lib/assets/manifest-v4.ts
var assetPresentationSchema = external_exports.object({
  schemaVersion: external_exports.literal(1),
  sourcePixelsPerWorldUnit: external_exports.union([external_exports.literal(1), external_exports.literal(2), external_exports.literal(4)])
}).strict();
var speciesManifestV4Schema = speciesManifestV3Schema.innerType().extend({
  schemaVersion: external_exports.literal(4),
  presentation: assetPresentationSchema
}).strict().superRefine((value, context) => {
  const legacy2 = { ...value };
  Reflect.deleteProperty(legacy2, "presentation");
  const result = speciesManifestV3Schema.safeParse({ ...legacy2, schemaVersion: 3 });
  if (!result.success) for (const issue of result.error.issues) context.addIssue(issue);
});

// src/lib/assets/intake-v3.ts
var assetPackagingInputV3Schema = assetPackagingInputV2Schema.innerType().extend({
  schemaVersion: external_exports.literal(3),
  presentation: assetPresentationSchema
}).strict().superRefine((value, context) => {
  const legacy2 = { ...value };
  Reflect.deleteProperty(legacy2, "presentation");
  const result = assetPackagingInputV2Schema.safeParse({ ...legacy2, schemaVersion: 2 });
  if (!result.success) for (const issue of result.error.issues) context.addIssue(issue);
});
var rgbaSourceArtifactV2Schema = rgbaSourceArtifactSchema.innerType().extend({
  schemaVersion: external_exports.literal(2),
  input: assetPackagingInputV3Schema
}).strict().superRefine((value, context) => {
  const legacy2 = { ...value.input };
  Reflect.deleteProperty(legacy2, "presentation");
  const result = rgbaSourceArtifactSchema.safeParse({
    ...value,
    schemaVersion: 1,
    input: { ...legacy2, schemaVersion: 2 }
  });
  if (!result.success) for (const issue of result.error.issues) context.addIssue(issue);
});
var supportedPosePackagingInputSchema = external_exports.union([
  assetPackagingInputV2Schema,
  assetPackagingInputV3Schema
]);
var supportedRgbaSourceArtifactSchema = external_exports.union([
  rgbaSourceArtifactSchema,
  rgbaSourceArtifactV2Schema
]);

// src/lib/workbench/pagination.ts
var WORKBENCH_PAGE_SIZE = 5;
var WORKBENCH_PAGE_MAX = 10;
var WORKBENCH_RESPONSE_BYTES = 8 * 1024 * 1024;
var pageCursorSchema = external_exports.string().min(1).max(512).regex(/^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$/);
var pageRequestSchema = external_exports.object({
  cursor: pageCursorSchema.optional(),
  limit: external_exports.number().int().min(1).max(WORKBENCH_PAGE_MAX).default(WORKBENCH_PAGE_SIZE)
}).strict();
var pageInfoSchema = external_exports.object({
  cursor: pageCursorSchema,
  nextCursor: pageCursorSchema.nullable(),
  limit: external_exports.number().int().min(1).max(WORKBENCH_PAGE_MAX)
}).strict();

// src/lib/pipeline/contracts.ts
var pipelineIdentifierSchema = external_exports.string().min(1).max(200).regex(/\S/);
var identifier3 = pipelineIdentifierSchema;
var integer3 = external_exports.number().int().nonnegative().max(Number.MAX_SAFE_INTEGER);
var pipelineVersionSchema = integer3.positive();
var version = pipelineVersionSchema;
var pipelineTimeSchema = integer3.max(864e13);
var time = pipelineTimeSchema;
var errorCode = external_exports.string().regex(/^[a-z0-9_-]{1,80}$/).nullable();
var jobStatusSchema = external_exports.enum([
  "queued",
  "running",
  "retry_wait",
  "blocked_provider",
  "awaiting_review",
  "completed",
  "failed",
  "cancelled"
]);
var stageStatusSchema = external_exports.enum([
  "pending",
  "running",
  "retry_wait",
  "blocked_provider",
  "succeeded",
  "failed",
  "cancelled"
]);
var artifactProvenanceSchema = external_exports.object({
  source: external_exports.enum(["deterministic_fixture", "provider", "user_upload"]),
  providerId: identifier3,
  providerVersion: identifier3,
  references: external_exports.array(external_exports.string()),
  fixture: external_exports.boolean(),
  license: external_exports.string().optional()
}).strict().superRefine((value, context) => {
  if (value.fixture !== (value.source === "deterministic_fixture"))
    context.addIssue({
      code: "custom",
      message: "Fixture provenance must identify a deterministic fixture."
    });
});
var reviewCommandSchema = external_exports.object({
  artifactId: identifier3,
  decision: external_exports.enum(["approved", "rejected"]),
  note: external_exports.string().max(1e3)
}).strict();
function pipelineSchemas(payload) {
  const queueJobSchema2 = external_exports.object({
    definitionId: identifier3,
    definitionVersion: version,
    input: payload,
    idempotencyKey: identifier3,
    parentJobId: identifier3.optional()
  }).strict();
  const jobFields = queueJobSchema2.extend({
    id: identifier3,
    ownerId: identifier3,
    rootJobId: identifier3,
    inputDigest: external_exports.string().regex(/^[a-f0-9]{64}$/),
    status: jobStatusSchema,
    createdAt: time,
    updatedAt: time,
    error: errorCode
  }).strict();
  const checkJob = (value, context) => {
    if (value.updatedAt < value.createdAt)
      context.addIssue({ code: "custom", message: "Job update predates creation." });
    if (value.parentJobId === value.id || !value.parentJobId && value.rootJobId !== value.id)
      context.addIssue({ code: "custom", message: "Invalid job ancestry." });
  };
  const pipelineJobSchema2 = jobFields.superRefine(checkJob);
  const stageRecordSchema2 = external_exports.object({
    jobId: identifier3,
    path: identifier3,
    version,
    ordinal: integer3.max(99),
    status: stageStatusSchema,
    attempts: integer3.max(10),
    maxAttempts: integer3.min(1).max(10),
    nextRunAt: time.nullable(),
    leaseUntil: time.nullable(),
    output: payload,
    error: errorCode
  }).strict().superRefine((value, context) => {
    if (value.attempts > value.maxAttempts)
      context.addIssue({ code: "custom", message: "Stage attempts exceed the retry policy." });
    if (value.status === "running" !== (value.leaseUntil !== null))
      context.addIssue({ code: "custom", message: "Stage lease does not match its state." });
    if (value.status === "running" && (value.attempts === 0 || value.nextRunAt !== null))
      context.addIssue({ code: "custom", message: "Running stage requires a claimed attempt." });
    if (value.status === "retry_wait" && value.nextRunAt === null)
      context.addIssue({ code: "custom", message: "Retry stage requires its next run time." });
  });
  const stageRunSchema2 = external_exports.object({
    id: identifier3,
    jobId: identifier3,
    stagePath: identifier3,
    attempt: integer3.min(1).max(10),
    status: external_exports.enum([
      "running",
      "succeeded",
      "failed",
      "expired",
      "cancelled",
      "blocked_provider"
    ]),
    startedAt: time,
    finishedAt: time.nullable(),
    error: errorCode
  }).strict().superRefine((value, context) => {
    if (value.status === "running" !== (value.finishedAt === null) || value.finishedAt !== null && value.finishedAt < value.startedAt)
      context.addIssue({
        code: "custom",
        message: "Run completion time does not match its state."
      });
  });
  const artifactDraftSchema2 = external_exports.object({
    family: identifier3,
    kind: identifier3,
    payload,
    provenance: artifactProvenanceSchema
  }).strict();
  const pipelineArtifactSchema2 = artifactDraftSchema2.extend({
    id: identifier3,
    ownerId: identifier3,
    jobId: identifier3,
    stagePath: identifier3,
    stageVersion: version,
    definitionId: identifier3,
    definitionVersion: version,
    inputDigest: external_exports.string().regex(/^[a-f0-9]{64}$/),
    contentDigest: external_exports.string().regex(/^[a-f0-9]{64}$/),
    version,
    createdAt: time,
    reviewStatus: external_exports.enum(["pending", "approved", "rejected"]),
    reviewedAt: time.nullable(),
    reviewNote: external_exports.string().max(1e3).nullable()
  }).strict().superRefine((value, context) => {
    if (value.reviewStatus === "pending" !== (value.reviewedAt === null) || value.reviewStatus === "pending" && value.reviewNote !== null || value.reviewedAt !== null && value.reviewedAt < value.createdAt)
      context.addIssue({
        code: "custom",
        message: "Artifact review evidence does not match its decision."
      });
  });
  const stageResultSchema2 = external_exports.object({ output: payload, artifacts: external_exports.array(artifactDraftSchema2).max(32).optional() }).strict();
  const workbenchJobSchema2 = jobFields.extend({
    stages: external_exports.array(stageRecordSchema2).max(100),
    artifacts: external_exports.array(pipelineArtifactSchema2).max(3200),
    artifactError: external_exports.string().max(2e3).nullable()
  }).strict().superRefine((value, context) => {
    checkJob(value, context);
    const paths = /* @__PURE__ */ new Set();
    for (const [ordinal, stage] of value.stages.entries()) {
      if (stage.jobId !== value.id || stage.ordinal !== ordinal || paths.has(stage.path))
        context.addIssue({
          code: "custom",
          message: "Stage identity or order does not match its job."
        });
      paths.add(stage.path);
    }
    const ids = /* @__PURE__ */ new Set();
    for (const artifact of value.artifacts) {
      const stage = value.stages.find((entry) => entry.path === artifact.stagePath);
      if (ids.has(artifact.id) || artifact.ownerId !== value.ownerId || artifact.jobId !== value.id || artifact.definitionId !== value.definitionId || artifact.definitionVersion !== value.definitionVersion || artifact.inputDigest !== value.inputDigest || !stage || stage.version !== artifact.stageVersion)
        context.addIssue({
          code: "custom",
          message: "Artifact identity does not match its job and stage."
        });
      ids.add(artifact.id);
    }
    if (value.artifactError !== null && value.artifacts.length)
      context.addIssue({
        code: "custom",
        message: "Corrupt artifact responses cannot include renderable artifacts."
      });
  });
  const jobsReadResponseSchema3 = external_exports.object({
    jobs: external_exports.array(workbenchJobSchema2).max(WORKBENCH_PAGE_MAX),
    page: pageInfoSchema.optional(),
    refreshError: external_exports.string().min(1).max(500).optional()
  }).strict();
  const jobsCommandResponseSchema3 = jobsReadResponseSchema3.extend({ message: external_exports.string().min(1).max(2e3) }).strict();
  return {
    jobsReadResponseSchema: jobsReadResponseSchema3,
    jobsCommandResponseSchema: jobsCommandResponseSchema3,
    queueJobSchema: queueJobSchema2,
    pipelineJobSchema: pipelineJobSchema2,
    stageRecordSchema: stageRecordSchema2,
    stageRunSchema: stageRunSchema2,
    artifactDraftSchema: artifactDraftSchema2,
    pipelineArtifactSchema: pipelineArtifactSchema2,
    stageResultSchema: stageResultSchema2,
    workbenchJobSchema: workbenchJobSchema2
  };
}
var {
  jobsReadResponseSchema,
  jobsCommandResponseSchema,
  queueJobSchema,
  pipelineJobSchema,
  stageRecordSchema,
  stageRunSchema,
  artifactDraftSchema,
  pipelineArtifactSchema,
  stageResultSchema,
  workbenchJobSchema
} = pipelineSchemas(jsonValueSchema);

// src/lib/assets/image-stage-contracts.ts
var id4 = external_exports.string().min(1).max(160).regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]*$/);
var sha256 = external_exports.string().regex(/^[a-f0-9]{64}$/);
var text = external_exports.string().min(1).max(2e3).refine((value) => value === value.trim(), "Reference metadata must already be normalized").refine(
  (value) => [...value].every(
    (character) => character >= " " && character !== "\x7F" && character !== "<" && character !== ">"
  ),
  "Reference metadata must be plain text"
);
var https = external_exports.string().max(2048).regex(/^https:\/\/[!-~]+(?![\s\S])/).refine((value) => {
  try {
    const url = new URL(value);
    return url.protocol === "https:" && !url.username && !url.password;
  } catch {
    return false;
  }
}, "Only credential-free HTTPS source identifiers are allowed");
var pointInTime = external_exports.string().datetime();
var review = external_exports.object({ reviewerId: id4, evidenceId: id4, reviewedAt: pointInTime }).strict();
var localReferenceSchema = external_exports.object({
  schemaVersion: external_exports.literal(1),
  id: id4,
  fixture: external_exports.boolean(),
  source: external_exports.object({
    kind: external_exports.enum(["local-file", "archive-file", "technical-fixture"]),
    fileIdentity: text,
    originalUrl: https.nullable(),
    descriptionPageUrl: https.nullable(),
    author: text,
    uploader: text.nullable(),
    attribution: text,
    description: text.nullable(),
    sourceTimestamp: pointInTime.nullable(),
    remoteHash: external_exports.object({
      algorithm: external_exports.enum(["sha1", "sha256"]),
      value: external_exports.string().regex(/^[a-f0-9]{40}([a-f0-9]{24})?$/)
    }).strict().nullable()
  }).strict(),
  original: external_exports.object({
    bytes: external_exports.number().int().min(1).max(16777216),
    sha256,
    mime: external_exports.enum(["image/png", "image/jpeg", "application/x-chirp-rgba8"])
  }).strict(),
  decoded: external_exports.object({
    format: external_exports.literal("rgba8-straight"),
    width: external_exports.number().int().min(1).max(256),
    height: external_exports.number().int().min(1).max(256),
    sha256,
    decoder: external_exports.object({ id: id4, version: id4 }).strict(),
    derivation: external_exports.enum(["raw-identity", "declared-unverified"])
  }).strict(),
  rights: external_exports.object({
    licenseId: id4,
    licenseVersion: id4,
    licenseUrl: https.nullable(),
    status: external_exports.enum(["pending", "approved", "denied", "conflicting"]),
    restrictions: external_exports.array(text).max(16),
    referenceUseAllowed: external_exports.boolean(),
    derivativesAllowed: external_exports.boolean(),
    redistributionAllowed: external_exports.boolean(),
    generationPermission: external_exports.enum(["not-reviewed", "allowed", "denied"]),
    review: review.nullable()
  }).strict(),
  taxonomy: external_exports.object({
    application: taxonomyIdentitySchema,
    declaredScientificName: text,
    aliases: external_exports.array(
      external_exports.object({ authority: id4, version: id4, taxonId: id4, scientificName: text }).strict()
    ).max(16),
    externalEvidence: external_exports.array(
      external_exports.object({
        authority: id4,
        version: id4,
        entityId: id4,
        statement: external_exports.enum(["scientific-name", "rank", "parent-taxon", "image", "depicts"]),
        value: text,
        status: external_exports.literal("candidate-evidence")
      }).strict()
    ).max(32),
    review: review.nullable()
  }).strict(),
  annotations: external_exports.object({
    sex: external_exports.enum(["female", "male", "unknown"]),
    age: external_exports.enum(["juvenile", "adult", "unknown"]),
    plumage: text.nullable(),
    viewpoint: external_exports.enum([
      "left",
      "right",
      "front",
      "back",
      "above",
      "below",
      "oblique",
      "unknown"
    ])
  }).strict()
}).strict().superRefine((value, context) => {
  const fail = (message) => context.addIssue({ code: "custom", message });
  if (value.source.kind === "technical-fixture" !== value.fixture)
    fail("Technical fixture status must match source kind.");
  if (value.source.kind === "archive-file" && (!value.source.originalUrl || !value.source.descriptionPageUrl))
    fail("Archive files require original and description-page identifiers.");
  const remote = value.source.remoteHash;
  if (remote && remote.value.length !== (remote.algorithm === "sha1" ? 40 : 64))
    fail("Remote hash length does not match its algorithm.");
  const aliases = value.taxonomy.aliases.map(
    (alias) => `${alias.authority}/${alias.version}/${alias.taxonId}`
  );
  if (new Set(aliases).size !== aliases.length) fail("Taxonomy alias pins must be unique.");
  if (value.fixture && value.taxonomy.review !== null)
    fail("A technical fixture cannot claim reviewed species fidelity.");
  if (value.original.mime === "application/x-chirp-rgba8" !== (value.decoded.derivation === "raw-identity"))
    fail(
      "Encoded photo decoding remains an unverified declaration until an adapter is implemented."
    );
});
var referencePolicySchema = external_exports.object({
  schemaVersion: external_exports.literal(1),
  id: id4,
  version: id4,
  use: external_exports.enum(["reference-only", "derived-sprite"]),
  allowedLicenses: external_exports.array(external_exports.object({ id: id4, version: id4, url: https.nullable() }).strict()).max(32),
  allowTechnicalFixtures: external_exports.boolean()
}).strict();
var byte = external_exports.number().int().min(0).max(255);
var channel = external_exports.array(byte).min(1).max(65536);
var coordinates = external_exports.object({ x: external_exports.number().int().min(0).max(256), y: external_exports.number().int().min(0).max(256) }).strict();
var contact = coordinates.extend({ kind: external_exports.enum(["left-foot", "right-foot", "ground", "perch"]) }).strict();
var stageIdentity = external_exports.object({ id: id4, version: id4 }).strict();
var segmentationStageSchema = external_exports.discriminatedUnion("encoding", [
  external_exports.object({
    encoding: external_exports.literal("binary-mask-u8"),
    values: external_exports.array(external_exports.union([external_exports.literal(0), external_exports.literal(255)])).min(1).max(65536),
    sha256,
    adapter: stageIdentity
  }).strict(),
  external_exports.object({
    encoding: external_exports.literal("logits-f32-le"),
    values: external_exports.array(external_exports.number().finite().min(-1e6).max(1e6)).min(1).max(65536),
    sha256,
    adapter: stageIdentity
  }).strict()
]);
var matteStageSchema = external_exports.object({
  encoding: external_exports.literal("alpha-u8"),
  alpha: channel,
  sha256,
  origin: external_exports.enum(["supplied-matte", "technical-fixture"]),
  adapter: stageIdentity
}).strict();
var foregroundStageSchema = external_exports.object({
  encoding: external_exports.literal("rgb8"),
  rgb: external_exports.array(byte).min(3).max(65536 * 3),
  sha256,
  alphaMode: external_exports.enum(["straight", "premultiplied"]),
  recovery: external_exports.enum(["supplied-recovered", "technical-fixture"]),
  adapter: stageIdentity
}).strict();
var imageFrameSchema = external_exports.object({
  id: id4,
  timestampUs: external_exports.number().int().min(0).max(Number.MAX_SAFE_INTEGER),
  durationUs: external_exports.number().int().min(1).max(6e7),
  sourceRgba: external_exports.array(byte).min(4).max(65536 * 4),
  sourceSha256: sha256,
  anchor: coordinates,
  contacts: external_exports.array(contact).max(4),
  segmentation: segmentationStageSchema.nullable(),
  matte: matteStageSchema,
  foreground: foregroundStageSchema
}).strict();
var imageStageSequenceSchema = external_exports.object({
  schemaVersion: external_exports.literal(1),
  fixture: external_exports.boolean(),
  canvas: external_exports.object({ width: external_exports.number().int().min(1).max(256), height: external_exports.number().int().min(1).max(256) }).strict(),
  frames: external_exports.array(imageFrameSchema).min(1).max(64),
  loop: external_exports.boolean(),
  // These are audit identities, not URLs, invocation settings, or an execution capability.
  referenceIds: external_exports.array(id4).min(1).max(16),
  modelSlot: external_exports.literal("unconfigured")
}).strict().superRefine((sequence, context) => {
  const fail = (message) => context.addIssue({ code: "custom", message });
  const { width, height } = sequence.canvas, pixels = width * height;
  if (pixels * sequence.frames.length > 65536)
    fail("Image sequence exceeds decoded pixel budget.");
  if (new Set(sequence.referenceIds).size !== sequence.referenceIds.length)
    fail("Reference IDs must be unique.");
  if (new Set(sequence.frames.map((frame) => frame.id)).size !== sequence.frames.length)
    fail("Frame IDs must be unique.");
  for (const [index, frame] of sequence.frames.entries()) {
    if (frame.sourceRgba.length !== pixels * 4 || frame.matte.alpha.length !== pixels || frame.foreground.rgb.length !== pixels * 3 || frame.segmentation && frame.segmentation.values.length !== pixels)
      fail("Every image stage must exactly match canvas dimensions.");
    if (frame.anchor.x > width || frame.anchor.y > height || frame.contacts.some((point3) => point3.x > width || point3.y > height))
      fail("Frame anchor/contact is outside its canvas.");
    if (new Set(frame.contacts.map((point3) => point3.kind)).size !== frame.contacts.length)
      fail("Contact kinds must be unique.");
    if (!Number.isSafeInteger(frame.timestampUs + frame.durationUs))
      fail("Frame end timestamp exceeds safe integer range.");
    const previous = sequence.frames[index - 1];
    if (previous && frame.timestampUs !== previous.timestampUs + previous.durationUs)
      fail("Frame timestamps must preserve contiguous original durations/order.");
    if (sequence.fixture !== (frame.matte.origin === "technical-fixture") || sequence.fixture !== (frame.foreground.recovery === "technical-fixture"))
      fail("Fixture stages cannot claim recovered photographic foreground.");
  }
});
var imageQaPolicySchema = external_exports.object({
  schemaVersion: external_exports.literal(1),
  id: id4,
  version: id4,
  edgeAlphaThreshold: byte.min(1),
  maxChangedEdgeFraction: external_exports.number().min(0).max(1),
  maxContactDriftPixels: external_exports.number().min(0).max(512),
  allowContactSetChange: external_exports.boolean()
}).strict();
var losslessPixelPolicySchema = external_exports.object({
  schemaVersion: external_exports.literal(1),
  id: id4,
  version: id4,
  alpha: external_exports.literal("binary-required"),
  palette: external_exports.literal("preserve"),
  logicalPixelSize: external_exports.number().int().min(1).max(16),
  paletteLimit: external_exports.number().int().min(1).max(64),
  crop: external_exports.literal("stable-union-including-anchors")
}).strict();

// src/lib/assets/animation-specification.ts
var hash4 = external_exports.string().regex(/^[a-f0-9]{64}$/);
var id5 = external_exports.string().regex(/^[a-zA-Z0-9][a-zA-Z0-9._:@-]{0,159}$/);
var text2 = external_exports.string().min(1).max(4e3);
var animationPlanningInputSchema = external_exports.object({
  schemaVersion: external_exports.literal(1),
  taxonomy: taxonomyIdentitySchema,
  scientificName: external_exports.string().min(3).max(160),
  references: external_exports.array(localReferenceSchema).max(16)
}).strict().superRefine((value, context) => {
  const fail = (message) => context.addIssue({ code: "custom", message });
  if (catalogEntry(value.taxonomy.speciesId)?.scientificName !== value.scientificName)
    fail("Scientific name must exactly match the pinned application catalog identity.");
  if (new Set(value.references.map((reference) => reference.id)).size !== value.references.length)
    fail("Planning reference IDs must be unique.");
  for (const reference of value.references)
    if (reference.taxonomy.application.speciesId !== value.taxonomy.speciesId || reference.taxonomy.declaredScientificName !== value.scientificName)
      fail("Reference identity must match the planned species and its scientific name.");
});
var frameSchema = external_exports.object({
  frame: animationPoseSchema.shape.frame,
  phase: external_exports.string().min(1).max(160),
  durationTicks: animationPoseSchema.shape.durationTicks,
  proposedPivot: pointSchema,
  contactRequirements: external_exports.array(contactSchema.shape.kind).max(4)
}).strict();
var clipSchema = external_exports.object({
  action: external_exports.enum(animationStates),
  direction: animationClipV3Schema.shape.direction,
  loop: external_exports.boolean(),
  completion: external_exports.enum(["repeat", "hold-final-pose"]),
  purpose: external_exports.string().min(1).max(300),
  frames: external_exports.array(frameSchema).min(1).max(64),
  entry: external_exports.literal("review-against-idle-support-and-silhouette"),
  exit: external_exports.literal("review-against-idle-support-and-silhouette"),
  loopReview: external_exports.enum(["last-to-first-pixels-pivot-contacts", "not-looping-review-terminal-hold"])
}).strict();
var animationSpecificationSchema = external_exports.object({
  schemaVersion: external_exports.literal(1),
  templateVersion: external_exports.literal("chirp-animation-prompts@1"),
  status: external_exports.literal("proposed"),
  canvas: external_exports.object({ width: external_exports.literal(32), height: external_exports.literal(32) }).strict(),
  logicalPixelSize: external_exports.literal(1),
  paletteLimit: external_exports.literal(32),
  alpha: external_exports.literal("binary-transparent-background"),
  ticksPerSecond: external_exports.literal(30),
  totalFrames: external_exports.number().int().min(1).max(64),
  decodedPixels: external_exports.number().int().min(1).max(65536),
  clips: external_exports.array(clipSchema).length(animationStates.length)
}).strict().superRefine((value, context) => {
  const fail = (message) => context.addIssue({ code: "custom", message });
  if (value.clips.some((clip3, index) => clip3.action !== animationStates[index]) || new Set(value.clips.map((clip3) => clip3.action)).size !== animationStates.length)
    fail("A production plan requires each canonical action once in canonical order.");
  const frames = value.clips.flatMap((clip3) => clip3.frames);
  if (frames.length !== value.totalFrames || frames.some((frame, index) => frame.frame !== index) || value.decodedPixels !== value.canvas.width * value.canvas.height * frames.length)
    fail("Frame inventory must be contiguous and match the exact decoded allocation.");
  for (const clip3 of value.clips) {
    if (clip3.loop && (clip3.completion !== "repeat" || clip3.loopReview !== "last-to-first-pixels-pivot-contacts") || !clip3.loop && (clip3.completion !== "hold-final-pose" || clip3.loopReview !== "not-looping-review-terminal-hold"))
      fail("Loop, completion and seam review requirements disagree.");
    for (const frame of clip3.frames)
      if (frame.proposedPivot.x > value.canvas.width || frame.proposedPivot.y > value.canvas.height || new Set(frame.contactRequirements).size !== frame.contactRequirements.length)
        fail("Proposed pivots must fit the canvas and contact requirements must be distinct.");
  }
});
var animationRecipeSchema = external_exports.object({
  schemaVersion: external_exports.literal(1),
  id: id5,
  version: external_exports.number().int().min(1).max(1e6),
  specification: animationSpecificationSchema
}).strict();
var frameOverrideSchema = external_exports.object({
  index: external_exports.number().int().min(0).max(63),
  phase: external_exports.string().regex(/^[a-z][a-z0-9-]{0,159}$/).optional(),
  durationTicks: animationPoseSchema.shape.durationTicks.optional(),
  proposedPivot: external_exports.object({ x: pointSchema.shape.x.max(32), y: pointSchema.shape.y.max(32) }).strict().optional(),
  contactRequirements: external_exports.array(contactSchema.shape.kind).max(4).optional()
}).strict().superRefine((value, context) => {
  if (Object.keys(value).length === 1)
    context.addIssue({
      code: "custom",
      message: "A frame override must explicitly change a field."
    });
  if (value.contactRequirements && new Set(value.contactRequirements).size !== value.contactRequirements.length)
    context.addIssue({
      code: "custom",
      message: "Override contact requirements must be distinct."
    });
});
var clipOverrideSchema = external_exports.object({
  action: external_exports.enum(animationStates),
  durationTicks: animationPoseSchema.shape.durationTicks.optional(),
  loop: external_exports.boolean().optional(),
  frames: external_exports.array(frameOverrideSchema).min(1).max(64).optional()
}).strict().superRefine((value, context) => {
  if (Object.keys(value).length === 1)
    context.addIssue({
      code: "custom",
      message: "A clip override must explicitly change a field."
    });
  if (value.frames && new Set(value.frames.map((frame) => frame.index)).size !== value.frames.length)
    context.addIssue({
      code: "custom",
      message: "Frame override indices must be unique within a clip."
    });
});
var animationPlanningInputV2Schema = external_exports.object({
  schemaVersion: external_exports.literal(2),
  taxonomy: taxonomyIdentitySchema,
  scientificName: external_exports.string().min(3).max(160),
  references: external_exports.array(localReferenceSchema).max(16),
  recipe: external_exports.object({ id: id5, version: animationRecipeSchema.shape.version }).strict(),
  overrides: external_exports.object({ clips: external_exports.array(clipOverrideSchema).max(animationStates.length) }).strict()
}).strict().superRefine((value, context) => {
  const identity = animationPlanningInputSchema.safeParse({
    schemaVersion: 1,
    taxonomy: value.taxonomy,
    scientificName: value.scientificName,
    references: value.references
  });
  if (!identity.success) for (const issue of identity.error.issues) context.addIssue(issue);
  if (new Set(value.overrides.clips.map((clip3) => clip3.action)).size !== value.overrides.clips.length)
    context.addIssue({ code: "custom", message: "Each clip can have only one override." });
});
var animationProductionPlanSchema = external_exports.object({
  schemaVersion: external_exports.literal(1),
  format: external_exports.literal("animation-production-plan"),
  execution: external_exports.literal("planning-only"),
  model: external_exports.literal("unconfigured"),
  generatedFrames: external_exports.literal(0),
  taxonFidelityReviewed: external_exports.literal(false),
  taxonomy: taxonomyIdentitySchema,
  scientificName: external_exports.string().min(3).max(160),
  inputSha256: hash4,
  specificationSha256: hash4,
  specification: animationSpecificationSchema,
  references: external_exports.array(
    external_exports.object({
      id: id5,
      originalSha256: hash4,
      decodedSha256: hash4,
      status: external_exports.literal("declared-not-byte-verified")
    }).strict()
  ).max(16),
  blockers: external_exports.array(
    external_exports.enum([
      "references-missing",
      "reference-bytes-unverified",
      "reference-is-fixture",
      "reference-rights-unreviewed",
      "generation-permission-unreviewed",
      "species-fidelity-unreviewed",
      "model-unconfigured",
      "art-direction-unapproved",
      "output-review-required"
    ])
  ).min(3).max(9),
  prompts: external_exports.array(
    external_exports.object({
      action: external_exports.enum(animationStates),
      templateVersion: external_exports.literal("chirp-animation-prompts@1"),
      prompt: text2,
      negativePrompt: text2,
      frames: external_exports.array(external_exports.object({ frame: animationPoseSchema.shape.frame, prompt: text2 }).strict()).min(1).max(64)
    }).strict()
  ).length(animationStates.length),
  limitations: external_exports.array(text2).min(1).max(16)
}).strict().superRefine((value, context) => {
  const fail = (message) => context.addIssue({ code: "custom", message });
  if (catalogEntry(value.taxonomy.speciesId)?.scientificName !== value.scientificName)
    fail("Plan scientific name must match its pinned catalog identity.");
  if (new Set(value.references.map((reference) => reference.id)).size !== value.references.length || new Set(value.blockers).size !== value.blockers.length)
    fail("Reference identities and blockers must be unique.");
  const required2 = [
    "reference-bytes-unverified",
    "species-fidelity-unreviewed",
    "model-unconfigured",
    "art-direction-unapproved",
    "output-review-required"
  ];
  if (required2.some((blocker) => !value.blockers.includes(blocker)))
    fail("A technical plan cannot remove mandatory unverified production gates.");
  if (!value.references.length !== value.blockers.includes("references-missing"))
    fail("Missing references must be disclosed exactly.");
  for (const [index, prompt] of value.prompts.entries()) {
    const clip3 = value.specification.clips[index];
    if (!clip3 || prompt.action !== clip3.action || prompt.frames.length !== clip3.frames.length || prompt.frames.some((frame, frameIndex) => frame.frame !== clip3.frames[frameIndex]?.frame))
      fail("Every proposed action and frame must have its matching ordered prompt.");
  }
});

// src/lib/pipeline/commands.ts
var identifier4 = pipelineIdentifierSchema.max(160);
var jobCommandV1Schema = external_exports.discriminatedUnion("action", [
  external_exports.object({
    action: external_exports.literal("plan-animation"),
    key: identifier4,
    input: animationPlanningInputSchema
  }).strict(),
  external_exports.object({
    action: external_exports.literal("revise-shape"),
    requestId: external_exports.string().uuid(),
    basePin: animationPinSchema,
    shape: shapeReviewSchema
  }).strict(),
  external_exports.object({
    action: external_exports.literal("package-asset"),
    key: identifier4,
    input: external_exports.union([assetPackagingInputSchema, assetPackagingInputV2Schema])
  }).strict(),
  external_exports.object({
    action: external_exports.literal("generate-asset"),
    key: identifier4,
    input: assetGenerationInputSchema
  }).strict(),
  external_exports.object({
    action: external_exports.literal("queue"),
    definition: external_exports.enum(["fixture-artwork", "photo-to-animation", "asset-packaging"]),
    key: identifier4
  }).strict(),
  external_exports.object({ action: external_exports.literal("advance"), jobId: identifier4 }).strict(),
  external_exports.object({ action: external_exports.literal("cancel"), jobId: identifier4 }).strict(),
  external_exports.object({
    action: external_exports.literal("review"),
    artifactId: identifier4,
    decision: external_exports.enum(["approved", "rejected"])
  }).strict()
]);
var jobCommandV2Schema = external_exports.discriminatedUnion("action", [
  external_exports.object({
    action: external_exports.literal("plan-animation"),
    key: identifier4,
    input: external_exports.union([animationPlanningInputSchema, animationPlanningInputV2Schema])
  }).strict(),
  ...jobCommandV1Schema.options.slice(1)
]);
var jobCommandSchema = external_exports.discriminatedUnion("action", [
  external_exports.object({
    action: external_exports.literal("package-asset"),
    key: identifier4,
    input: external_exports.union([
      assetPackagingInputSchema,
      assetPackagingInputV2Schema,
      assetPackagingInputV3Schema
    ])
  }).strict(),
  ...jobCommandV2Schema.options.filter((option) => option.shape.action.value !== "package-asset")
]);

// src/lib/contracts/generated/json-value-v1.validator.js
var json_value_v1_validator_default = validate10;
var wrapper0 = { validate: validate11 };
function validate11(data, { instancePath = "", parentData, parentDataProperty, rootData = data } = {}) {
  let vErrors = null;
  let errors = 0;
  const _errs0 = errors;
  let valid0 = false;
  const _errs1 = errors;
  if (typeof data !== "string") {
    const err0 = {
      instancePath,
      schemaPath: "#/anyOf/0/type",
      keyword: "type",
      params: { type: "string" },
      message: "must be string"
    };
    if (vErrors === null) {
      vErrors = [err0];
    } else {
      vErrors.push(err0);
    }
    errors++;
  }
  var _valid0 = _errs1 === errors;
  valid0 = valid0 || _valid0;
  if (!valid0) {
    const _errs3 = errors;
    if (!(typeof data == "number" && isFinite(data))) {
      const err1 = {
        instancePath,
        schemaPath: "#/anyOf/1/type",
        keyword: "type",
        params: { type: "number" },
        message: "must be number"
      };
      if (vErrors === null) {
        vErrors = [err1];
      } else {
        vErrors.push(err1);
      }
      errors++;
    }
    var _valid0 = _errs3 === errors;
    valid0 = valid0 || _valid0;
    if (!valid0) {
      const _errs5 = errors;
      if (typeof data !== "boolean") {
        const err2 = {
          instancePath,
          schemaPath: "#/anyOf/2/type",
          keyword: "type",
          params: { type: "boolean" },
          message: "must be boolean"
        };
        if (vErrors === null) {
          vErrors = [err2];
        } else {
          vErrors.push(err2);
        }
        errors++;
      }
      var _valid0 = _errs5 === errors;
      valid0 = valid0 || _valid0;
      if (!valid0) {
        const _errs7 = errors;
        if (data !== null) {
          const err3 = {
            instancePath,
            schemaPath: "#/anyOf/3/type",
            keyword: "type",
            params: { type: "null" },
            message: "must be null"
          };
          if (vErrors === null) {
            vErrors = [err3];
          } else {
            vErrors.push(err3);
          }
          errors++;
        }
        var _valid0 = _errs7 === errors;
        valid0 = valid0 || _valid0;
        if (!valid0) {
          const _errs9 = errors;
          if (errors === _errs9) {
            if (Array.isArray(data)) {
              var valid1 = true;
              const len0 = data.length;
              for (let i0 = 0; i0 < len0; i0++) {
                const _errs11 = errors;
                if (!wrapper0.validate(data[i0], {
                  instancePath: instancePath + "/" + i0,
                  parentData: data,
                  parentDataProperty: i0,
                  rootData
                })) {
                  vErrors = vErrors === null ? wrapper0.validate.errors : vErrors.concat(wrapper0.validate.errors);
                  errors = vErrors.length;
                }
                var valid1 = _errs11 === errors;
                if (!valid1) {
                  break;
                }
              }
            } else {
              const err4 = {
                instancePath,
                schemaPath: "#/anyOf/4/type",
                keyword: "type",
                params: { type: "array" },
                message: "must be array"
              };
              if (vErrors === null) {
                vErrors = [err4];
              } else {
                vErrors.push(err4);
              }
              errors++;
            }
          }
          var _valid0 = _errs9 === errors;
          valid0 = valid0 || _valid0;
          if (!valid0) {
            const _errs12 = errors;
            if (errors === _errs12) {
              if (data && typeof data == "object" && !Array.isArray(data)) {
                for (const key0 in data) {
                  const _errs15 = errors;
                  if (!wrapper0.validate(data[key0], {
                    instancePath: instancePath + "/" + key0.replace(/~/g, "~0").replace(/\//g, "~1"),
                    parentData: data,
                    parentDataProperty: key0,
                    rootData
                  })) {
                    vErrors = vErrors === null ? wrapper0.validate.errors : vErrors.concat(wrapper0.validate.errors);
                    errors = vErrors.length;
                  }
                  var valid2 = _errs15 === errors;
                  if (!valid2) {
                    break;
                  }
                }
              } else {
                const err5 = {
                  instancePath,
                  schemaPath: "#/anyOf/5/type",
                  keyword: "type",
                  params: { type: "object" },
                  message: "must be object"
                };
                if (vErrors === null) {
                  vErrors = [err5];
                } else {
                  vErrors.push(err5);
                }
                errors++;
              }
            }
            var _valid0 = _errs12 === errors;
            valid0 = valid0 || _valid0;
          }
        }
      }
    }
  }
  if (!valid0) {
    const err6 = {
      instancePath,
      schemaPath: "#/anyOf",
      keyword: "anyOf",
      params: {},
      message: "must match a schema in anyOf"
    };
    if (vErrors === null) {
      vErrors = [err6];
    } else {
      vErrors.push(err6);
    }
    errors++;
    validate11.errors = vErrors;
    return false;
  } else {
    errors = _errs0;
    if (vErrors !== null) {
      if (_errs0) {
        vErrors.length = _errs0;
      } else {
        vErrors = null;
      }
    }
  }
  validate11.errors = vErrors;
  return errors === 0;
}
function validate10(data, { instancePath = "", parentData, parentDataProperty, rootData = data } = {}) {
  let vErrors = null;
  let errors = 0;
  if (!validate11(data, { instancePath, parentData, parentDataProperty, rootData })) {
    vErrors = vErrors === null ? validate11.errors : vErrors.concat(validate11.errors);
    errors = vErrors.length;
  }
  validate10.errors = vErrors;
  return errors === 0;
}

// src/lib/contracts/json-value.ts
function isJsonValue(value) {
  const active = /* @__PURE__ */ new WeakSet();
  const pending = [{ kind: "enter", value }];
  try {
    while (pending.length) {
      const current = pending.pop();
      if (!current) break;
      if (current.kind === "leave") {
        active.delete(current.value);
        continue;
      }
      const item = current.value;
      if (item === null || typeof item !== "object") continue;
      if (item instanceof Date || item instanceof Map || item instanceof Set) return false;
      const then = Reflect.get(item, "then");
      const catchValue = Reflect.get(item, "catch");
      if (typeof then === "function" && typeof catchValue === "function") return false;
      if (active.has(item)) return false;
      active.add(item);
      pending.push({ kind: "leave", value: item });
      for (const key in item) {
        const child = Reflect.get(item, key);
        if (child !== null && typeof child === "object") {
          pending.push({ kind: "enter", value: child });
        }
      }
    }
    return json_value_v1_validator_default(value);
  } catch {
    return false;
  }
}

// src/lib/http/command-error-contracts.ts
var domainErrorCodeSchema = external_exports.enum([
  "NOT_FOUND",
  "CONFLICT",
  "INVALID",
  "SCHEMA_VERSION",
  "STALE_PLACEMENT",
  "EVIDENCE_CONFLICT",
  "pipeline_conflict",
  "pipeline_not_found"
]);
var safeErrorTextSchema = external_exports.string().min(1).max(2e3).refine(
  (text3) => [...text3].every((character) => {
    const code = character.charCodeAt(0);
    return code >= 32 && code !== 127 || code === 9 || code === 10 || code === 13;
  })
);
var base = { schemaVersion: external_exports.literal(1), kind: external_exports.literal("request.command-error") };
var commandErrorSchema = external_exports.union([
  external_exports.object({
    ...base,
    code: external_exports.literal("REQUEST_FAILED"),
    error: external_exports.literal("The request could not be completed. Please retry.")
  }).strict(),
  external_exports.object({
    ...base,
    code: external_exports.literal("INVALID_COMMAND"),
    error: external_exports.literal("The request is not valid. Check the supplied fields and try again.")
  }).strict(),
  external_exports.object({ ...base, code: domainErrorCodeSchema, error: safeErrorTextSchema }).strict()
]);

// src/lib/http/request-budget-contracts.ts
var base2 = {
  schemaVersion: external_exports.literal(1),
  kind: external_exports.literal("request.budget-error"),
  retryAfterSeconds: external_exports.number().int().min(1).max(60)
};
var requestBudgetErrorSchema = external_exports.discriminatedUnion("code", [
  external_exports.object({
    ...base2,
    code: external_exports.literal("RATE_LIMITED"),
    error: external_exports.literal("Too many requests. Wait briefly, then retry.")
  }).strict(),
  external_exports.object({
    ...base2,
    code: external_exports.literal("SERVER_BUSY"),
    error: external_exports.literal("The server is busy. Wait briefly, then retry.")
  }).strict()
]);

// src/lib/assets/manifest.ts
var speciesManifestSchema = external_exports.union([
  speciesManifestV2Schema,
  speciesManifestV3Schema,
  speciesManifestV4Schema
]);

// src/lib/assets/registry.ts
var assetEntrySchema = external_exports.object({
  artworkId: external_exports.string().min(1).max(160),
  pin: animationPinSchema.optional(),
  catalogPin: catalogPinSchema.optional(),
  catalogStatus: external_exports.enum(["available", "revoked", "unavailable"]).optional(),
  status: external_exports.enum(["ready", "legacy", "unavailable"]),
  manifest: speciesManifestSchema.optional()
}).strict().superRefine((entry, context) => {
  if (entry.status === "ready" && (!entry.pin && !entry.catalogPin || !entry.manifest))
    context.addIssue({
      code: "custom",
      message: "Ready assets require a pin and a valid manifest."
    });
  if (entry.pin && entry.catalogPin || entry.catalogStatus !== void 0 && !entry.catalogPin || entry.catalogPin && (entry.status === "legacy" || entry.catalogStatus === void 0 || (entry.status === "ready" ? entry.catalogStatus !== "available" || entry.manifest?.schemaVersion !== 2 : entry.catalogStatus === "available")))
    context.addIssue({
      code: "custom",
      message: "Catalog availability must match one exact shared pin. Shared catalog renders support only version 2; private pose manifests require a private animation pin."
    });
  if (entry.status !== "ready" && entry.manifest)
    context.addIssue({
      code: "custom",
      message: "Unavailable assets cannot claim renderable content."
    });
});

// src/lib/pipeline/admission.ts
var checkedJsonSchema = external_exports.unknown().transform((value, context) => {
  if (isJsonValue(value)) return value;
  context.addIssue({ code: "custom", message: "Expected finite JSON data." });
  return external_exports.NEVER;
});
var admittedPipeline = pipelineSchemas(checkedJsonSchema);

// src/lib/client/contracts.ts
var yardResponse = external_exports.object({ snapshot: yardSnapshotSchema, assets: external_exports.array(assetEntrySchema) }).strict();
function validateAssets(value, context) {
  if (new Set(value.assets.map((entry) => entry.artworkId)).size !== value.assets.length)
    context.addIssue({ code: "custom", path: ["assets"], message: "Duplicate asset selection." });
  const selected = new Set(value.snapshot.birds.map((bird) => bird.artworkId));
  for (const entry of value.assets) {
    const artwork = value.snapshot.artworks.find((art) => art.id === entry.artworkId);
    if (!artwork || !selected.has(entry.artworkId)) {
      context.addIssue({
        code: "custom",
        path: ["assets"],
        message: "Unselected asset in yard response."
      });
      continue;
    }
    if (entry.status === "ready" && (entry.manifest?.speciesId !== artwork.speciesId || canonicalJson(entry.pin) !== canonicalJson(artwork.animationPin)))
      context.addIssue({
        code: "custom",
        path: ["assets"],
        message: "Resolved asset does not match the saved species and version pin."
      });
  }
}
var yardReadResponseSchema = yardResponse.superRefine(validateAssets);
var yardCommandResponseSchema = yardResponse.extend({ message: external_exports.string().min(1).max(2e3) }).strict().superRefine(validateAssets);
var jobsReadResponseSchema2 = admittedPipeline.jobsReadResponseSchema;
var jobsCommandResponseSchema2 = admittedPipeline.jobsCommandResponseSchema;
var legacyDomainError = external_exports.object({ error: safeErrorTextSchema, code: domainErrorCodeSchema }).strict();
var legacyConflictError = yardResponse.extend({ error: safeErrorTextSchema, code: external_exports.enum(["STALE_PLACEMENT", "EVIDENCE_CONFLICT"]) }).strict().superRefine(validateAssets);
var frameworkError = external_exports.object({
  message: external_exports.enum([
    "Production authentication is not configured. Development identity is disabled.",
    "Choose a development identity first.",
    "Your session has ended. Sign in again to continue.",
    "The request length is not valid.",
    "This request exceeds the allowed size.",
    "A request body is required.",
    "The request body timed out.",
    "A same-origin request is required.",
    "Use application/json.",
    "The JSON is not valid.",
    "The request must contain valid UTF-8.",
    "The request could not be completed. Please retry."
  ])
}).strict();

// src/lib/client/service.ts
var InvalidServiceResponse = class extends Error {
  constructor() {
    super("The server returned an invalid response. Keep the last confirmed state and refresh.");
  }
};
var SERVICE_RESPONSE_MAX_BYTES = 16 * 1024 * 1024;
var SERVICE_RESPONSE_TIMEOUT_MS = 45e3;
async function decodedResponse(source, acceptErrorStatus) {
  const controller = new AbortController();
  const deadline = performance.now() + SERVICE_RESPONSE_TIMEOUT_MS;
  let rejectAbort = () => void 0;
  const aborted = new Promise((_resolve, reject) => {
    rejectAbort = () => reject(new InvalidServiceResponse());
  });
  controller.signal.addEventListener("abort", rejectAbort, { once: true });
  const timer = setTimeout(() => controller.abort(), SERVICE_RESPONSE_TIMEOUT_MS);
  let response;
  let reader;
  let drained = false;
  function checkDeadline() {
    if (performance.now() >= deadline) controller.abort();
    controller.signal.throwIfAborted();
  }
  try {
    response = await Promise.race([
      source(controller.signal).then((value) => {
        if (controller.signal.aborted) {
          void value.body?.cancel().catch(() => void 0);
          throw new InvalidServiceResponse();
        }
        return value;
      }),
      aborted
    ]);
    reader = response.body?.getReader();
    if (response.status !== 200 && !(acceptErrorStatus && !response.ok))
      throw new InvalidServiceResponse();
    const declared = response.headers.get("content-length");
    if (declared !== null && (!/^\d+$/.test(declared) || !Number.isSafeInteger(Number(declared)) || Number(declared) > SERVICE_RESPONSE_MAX_BYTES))
      throw new InvalidServiceResponse();
    let bytes2 = 0, text3 = "";
    const decoder = new TextDecoder("utf-8", { fatal: true });
    if (reader) {
      while (true) {
        checkDeadline();
        const chunk = await Promise.race([reader.read(), aborted]);
        if (chunk.done) break;
        bytes2 += chunk.value.byteLength;
        if (bytes2 > SERVICE_RESPONSE_MAX_BYTES) throw new InvalidServiceResponse();
        text3 += decoder.decode(chunk.value, { stream: true });
      }
    }
    drained = true;
    checkDeadline();
    const input = JSON.parse(text3 + decoder.decode());
    checkDeadline();
    return { response, input, bodyDecoded: true };
  } catch {
    if (acceptErrorStatus && response && !response.ok)
      return { response, input: null, bodyDecoded: false };
    throw new InvalidServiceResponse();
  } finally {
    clearTimeout(timer);
    controller.signal.removeEventListener("abort", rejectAbort);
    if (!drained) controller.abort();
    if (reader) {
      if (!drained) void reader.cancel().catch(() => void 0);
      reader.releaseLock();
    }
  }
}
async function parseResponse(response, schema) {
  const { input } = await decodedResponse(() => Promise.resolve(response), false);
  const parsed = schema.safeParse(input);
  if (!parsed.success) throw new InvalidServiceResponse();
  return parsed.data;
}

// ../runtime-query-evidence/probes.ts
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
var out = process.argv[2];
var measurements = JSON.parse(readFileSync(join(out, "measurements.json"), "utf8"));
var evidence = { transport: [], originValidation: [], limit: SERVICE_RESPONSE_MAX_BYTES, source: "Exact repository + client parseResponse; in-process Response only, no HTTP server/browser." };
for (const count of [100, 3e4]) {
  const yard2 = new YardRepository(join(measurements.storage, `owner-${count}.sqlite`));
  const snapshot = yard2.rename("audit-owner", "audit-bird", "Committed audit rename", "2026-10-12T12:00:00.000Z");
  const stored = yard2.database.prepare("SELECT data FROM yard_owners WHERE owner_id=?").get("audit-owner").data;
  for (const command of [false, true]) {
    const payload = JSON.stringify({ snapshot, assets: [], ...command ? { message: "Saved to your yard." } : {} });
    for (const declared of [false, true]) {
      const headers = { "content-type": "application/json" };
      if (declared) headers["content-length"] = String(Buffer.byteLength(payload));
      let failure = null, accepted = false;
      const start = performance.now();
      try {
        await parseResponse(new Response(payload, { status: 200, headers }), command ? yardCommandResponseSchema : yardReadResponseSchema);
        accepted = true;
      } catch (error) {
        failure = { name: error.constructor.name, message: error.message };
      }
      evidence.transport.push({ events: count, command, declaredLength: declared, status: 200, storedBytes: Buffer.byteLength(stored), responseBytes: Buffer.byteLength(payload), accepted, failure, elapsedMs: performance.now() - start, committedName: JSON.parse(stored).birds[0].name });
    }
  }
  yard2.close();
}
var yard = new YardRepository(join(measurements.storage, "owner-10000.sqlite"));
var raw = JSON.parse(yard.database.prepare("SELECT data FROM yard_owners WHERE owner_id=?").get("audit-owner").data);
for (const count of [1, 100, 1e3]) {
  for (const linked of [false, true]) {
    const data = { ...raw, birds: Array.from({ length: count }, (_, index) => ({ ...raw.birds[0], id: `origin-audit:${index}`, originEventId: linked ? raw.events[raw.events.length - 1 - index].id : null })) };
    yardDataSchema.parse(data);
    const samples = [];
    for (let i = 0; i < 3; i++) {
      const start = performance.now();
      yardDataSchema.parse(data);
      samples.push(performance.now() - start);
    }
    evidence.originValidation.push({ events: data.events.length, residents: count, linkedLateOrigins: linked, samplesMs: samples, medianMs: [...samples].sort((a, b) => a - b)[1] });
  }
}
yard.close();
writeFileSync(join(out, "probes.json"), JSON.stringify(evidence, null, 2) + "\n");
console.log(JSON.stringify(evidence, null, 2));
