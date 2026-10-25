var __defProp = Object.defineProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
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
  const { data, path: path2, errorMaps, issueData } = params;
  const fullPath = [...path2, ...issueData.path || []];
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
  constructor(parent, value, path2, key) {
    this._cachedPath = [];
    this.parent = parent;
    this.data = value;
    this._path = path2;
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
function isValidIP(ip, version) {
  if ((version === "v4" || !version) && ipv4Regex.test(ip)) {
    return true;
  }
  if ((version === "v6" || !version) && ipv6Regex.test(ip)) {
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
function isValidCidr(ip, version) {
  if ((version === "v4" || !version) && ipv4CidrRegex.test(ip)) {
    return true;
  }
  if ((version === "v6" || !version) && ipv6CidrRegex.test(ip)) {
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
function mergeValues(a2, b2) {
  const aType = getParsedType(a2);
  const bType = getParsedType(b2);
  if (a2 === b2) {
    return { valid: true, data: a2 };
  } else if (aType === ZodParsedType.object && bType === ZodParsedType.object) {
    const bKeys = util.objectKeys(b2);
    const sharedKeys = util.objectKeys(a2).filter((key) => bKeys.indexOf(key) !== -1);
    const newObj = { ...a2, ...b2 };
    for (const key of sharedKeys) {
      const sharedValue = mergeValues(a2[key], b2[key]);
      if (!sharedValue.valid) {
        return { valid: false };
      }
      newObj[key] = sharedValue.data;
    }
    return { valid: true, data: newObj };
  } else if (aType === ZodParsedType.array && bType === ZodParsedType.array) {
    if (a2.length !== b2.length) {
      return { valid: false };
    }
    const newArray = [];
    for (let index = 0; index < a2.length; index++) {
      const itemA = a2[index];
      const itemB = b2[index];
      const sharedValue = mergeValues(itemA, itemB);
      if (!sharedValue.valid) {
        return { valid: false };
      }
      newArray.push(sharedValue.data);
    }
    return { valid: true, data: newArray };
  } else if (aType === ZodParsedType.date && bType === ZodParsedType.date && +a2 === +b2) {
    return { valid: true, data: a2 };
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
        const base = this._def.schema._parseSync({
          data: ctx.data,
          path: ctx.path,
          parent: ctx
        });
        if (!isValid(base))
          return INVALID;
        const result = effect.transform(base.value, checkCtx);
        if (result instanceof Promise) {
          throw new Error(`Asynchronous transform encountered during synchronous parse operation. Use .parseAsync instead.`);
        }
        return { status: status.value, value: result };
      } else {
        return this._def.schema._parseAsync({ data: ctx.data, path: ctx.path, parent: ctx }).then((base) => {
          if (!isValid(base))
            return INVALID;
          return Promise.resolve(effect.transform(base.value, checkCtx)).then((result) => ({
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
  static create(a2, b2) {
    return new _ZodPipeline({
      in: a2,
      out: b2,
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
}).strict().refine((b2) => b2.left < b2.right && b2.top < b2.bottom, "Zones must have positive area.");
var containsPoint = (b2, x, y) => x >= b2.left && x <= b2.right && y >= b2.top && y <= b2.bottom;
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
  if (new Set(references).size !== 3 || references.some((id) => !assets.has(id)))
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
var sameValue = (a2, b2) => a2.speciesId === b2.speciesId && (a2.observedAt === b2.observedAt || a2.observedAt !== null && b2.observedAt !== null && Date.parse(a2.observedAt) === Date.parse(b2.observedAt));
var sameRevision = (a2, b2) => a2.correctionId === b2.correctionId && sameValue(a2, b2);

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
    [...objects].sort((a2, b2) => a2.id.localeCompare(b2.id)).map(({ id, kind, x, y }) => [id, kind, x, y])
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
  const a2 = objectFootprint(first), b2 = objectFootprint(second);
  return a2.left < b2.right + OBJECT_CLEARANCE && a2.right + OBJECT_CLEARANCE > b2.left && a2.top < b2.bottom + OBJECT_CLEARANCE && a2.bottom + OBJECT_CLEARANCE > b2.top;
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
    (a2, b2) => (a2.x - desired.x) ** 2 + (a2.y - desired.y) ** 2 - ((b2.x - desired.x) ** 2 + (b2.y - desired.y) ** 2) || a2.y - b2.y || a2.x - b2.x
  );
}
function findObjectPlacement(kind, objects, setting, desired = { x: WORLD_WIDTH / 2, y: 430 }) {
  objectKindSchema.parse(kind);
  for (const point2 of placementCandidates(kind, setting, desired)) {
    const candidate = { id: "placement-candidate", kind, ...point2 };
    if (isPlacementValid(
      candidate,
      objects.filter((object) => object.id !== "placement-candidate"),
      setting
    ) && !objects.some((other) => objectsOverlap(candidate, other)))
      return point2;
  }
  return null;
}
function reanchorObjects(input, setting) {
  const objects = yardObjectsSchema.parse(input);
  let placed = objects.filter((object) => isPlacementValid(object, objects, setting));
  const retained = new Set(placed.map((object) => object.id));
  const ordered = [...objects].sort(
    (a2, b2) => OBJECT_CATALOG[b2.kind].width * OBJECT_CATALOG[b2.kind].depth - OBJECT_CATALOG[a2.kind].width * OBJECT_CATALOG[a2.kind].depth || a2.id.localeCompare(b2.id)
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
        (a2, b2) => (a2.x - object.x) ** 2 + (a2.y - object.y) ** 2 - ((b2.x - object.x) ** 2 + (b2.y - object.y) ** 2) || a2.y - b2.y || a2.x - b2.x
      );
      const position = cells.find(
        (point2) => isPlacementValid({ ...object, ...point2 }, placed, setting)
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
  for (const [label, values] of Object.entries({
    species: state.species,
    events: state.events,
    corrections: state.corrections,
    collection: state.collection,
    birds: state.birds,
    artworks: state.artworks
  })) {
    if (new Set(values.map((value) => value.id)).size !== values.length)
      fail(`Duplicate ${label} ID`);
  }
  const species = new Map(state.species.map((s) => [s.id, s]));
  const art = new Map(state.artworks.map((a2) => [a2.id, a2]));
  if (new Set(state.species.map((s) => s.scientificName.toLowerCase())).size !== state.species.length)
    fail("Duplicate taxon identity");
  if (new Set(state.events.map(sourceEventKey)).size !== state.events.length)
    fail("Duplicate source event identity");
  if (new Set(state.collection.map((entry) => entry.speciesId)).size !== state.collection.length)
    fail("Duplicate collection species");
  if (new Set(state.artworks.map((a2) => `${a2.speciesId}:${a2.version}`)).size !== state.artworks.length)
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
  const evidence = Object.fromEntries(
    Object.entries(event).filter(([key]) => key !== "ingestedAt")
  );
  return canonicalJson(evidence);
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
function snapshotOf(data, now2) {
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
      (bird) => bird.lifecycle === "temporary" && Date.parse(bird.expiresAt) <= Date.parse(now2) ? { ...bird, lifecycle: "expired" } : bird
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
  const { findings, effectiveEvidence, ...raw } = snapshot;
  const parsed = yardDataSchema.safeParse(raw);
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
function availableSpecies(data) {
  const choices = data.species.map(({ id, commonName, scientificName }) => ({
    id,
    commonName,
    scientificName
  }));
  for (const [id, species] of Object.entries(displayCatalog)) {
    if (!choices.some(
      (entry) => entry.id === id || entry.scientificName.toLowerCase() === species.scientificName.toLowerCase()
    ))
      choices.push({ id, commonName: species.commonName, scientificName: species.scientificName });
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
function migrateV1(input, now2 = (/* @__PURE__ */ new Date()).toISOString()) {
  timestampSchema.parse(now2);
  const legacy = legacySchema.parse(input);
  for (const [key, species] of Object.entries(legacy.species))
    if (key !== species.id) throw new YardValidationError("legacySpeciesIdentity");
  for (const [key, art] of Object.entries(legacy.artworks))
    if (key !== art.id || art.referencePhoto.speciesId !== art.speciesId)
      throw new YardValidationError("legacyArtworkIdentity");
  const stripSpecies = (species) => species;
  return yardDataSchema.parse({
    version: 2,
    species: Object.values(legacy.species).map(stripSpecies),
    events: legacy.identifications.map((event) => ({
      schemaVersion: 2,
      id: event.id,
      species: stripSpecies(event.species),
      observedAt: event.observedAt,
      ingestedAt: now2,
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
    collection: legacy.residents.map((bird) => ({
      id: bird.id,
      speciesId: bird.speciesId,
      collectedAt: bird.savedAt
    })),
    birds: legacy.residents.map((bird) => ({
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
    artworks: Object.values(legacy.artworks).map(
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
    preferences: { ...defaultPreferences(), ...legacy.preferences }
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
var normalizeNow = (now2) => new Date(timestampSchema.parse(now2)).toISOString();
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
    const version = external_exports.object({ version: external_exports.number().int().positive().safe().nullable() }).parse(this.database.prepare("SELECT MAX(version) AS version FROM yard_migrations").get()).version ?? 0;
    if (version > 1)
      throw new YardError(
        "SCHEMA_VERSION",
        "Database is newer than this application; downgrade refused."
      );
    if (version < 1)
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
      const name = `yard_operation_${++this.savepointSequence}`;
      this.database.exec(`SAVEPOINT ${name}`);
      try {
        const result = action();
        this.database.exec(`RELEASE SAVEPOINT ${name}`);
        return result;
      } catch (error) {
        this.database.exec(`ROLLBACK TO SAVEPOINT ${name}`);
        this.database.exec(`RELEASE SAVEPOINT ${name}`);
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
  snapshot(ownerId, now2 = nowIso()) {
    return snapshotOf(this.read(ownerId), normalizeNow(now2));
  }
  importEvents(ownerId, input, now2 = nowIso()) {
    const serverNow = normalizeNow(now2);
    const batch = Array.isArray(input) ? input : [input];
    if (batch.length > 1e3)
      throw new YardError("INVALID", "Import at most 1000 events per batch.");
    const incoming = batch.map((item) => importEventSchema.parse(item));
    return this.mutate(ownerId, (state) => this.insertEvents(ownerId, state, incoming, serverNow));
  }
  insertEvents(ownerId, state, incoming, serverNow) {
    let inserted = 0;
    let duplicates = 0;
    for (const raw of incoming) {
      const event = { ...raw, ingestedAt: serverNow };
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
  addManualFinding(ownerId, input, now2 = nowIso()) {
    now2 = normalizeNow(now2);
    const finding = manualFindingSchema.parse(input);
    return this.mutate(
      ownerId,
      (state) => {
        const id = `manual:${finding.id}`;
        return this.insertEvents(
          ownerId,
          state,
          [
            {
              schemaVersion: 2,
              id,
              species: this.knownSpecies(state, finding.speciesId),
              observedAt: finding.observedAt === null ? null : new Date(finding.observedAt).toISOString(),
              source: { kind: "manual", label: "Manual entry", sourceEventId: id },
              metadata: { manualEntryVersion: 1, note: finding.note }
            }
          ],
          now2
        );
      },
      (result) => {
        if (result.inserted === 1)
          this.hooks.manualInserted?.(ownerId, `manual:${finding.id}`, now2);
      }
    );
  }
  /** Appends only; a retry checks its immutable receipt before checking the current revision. */
  correctEvents(ownerId, input, now2 = nowIso()) {
    now2 = normalizeNow(now2);
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
        state.corrections.push({ ...correction, recordedAt: now2 });
        inserted++;
      }
      return { inserted, duplicates, snapshot: snapshotOf(state, now2) };
    });
  }
  selectableArtwork(ownerId, artwork, state) {
    return this.hooks.artworkSelectable?.(
      ownerId,
      artwork,
      state.species.find((species) => species.id === artwork.speciesId)
    ) ?? true;
  }
  visit(ownerId, state, event, now2) {
    if (!event.observedAt) return;
    const observed = Date.parse(event.observedAt);
    const current = Date.parse(now2);
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
    ).sort((a2, b2) => b2.version - a2.version)[0];
    state.birds.push({
      id: randomUUID(),
      speciesId: event.species.id,
      name: null,
      lifecycle: "temporary",
      createdAt: now2,
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
  collect(state, speciesId, now2) {
    idSchema.parse(speciesId);
    if (!state.species.some((s) => s.id === speciesId))
      throw new YardError("NOT_FOUND", "Species not found in this collection.");
    if (!state.collection.some((entry) => entry.speciesId === speciesId))
      state.collection.push({ id: randomUUID(), speciesId, collectedAt: now2 });
  }
  promote(ownerId, birdId, name, now2 = nowIso()) {
    now2 = normalizeNow(now2);
    return this.mutate(ownerId, (state) => {
      const bird = this.bird(state, birdId);
      if (name !== void 0) bird.name = this.validName(name);
      bird.lifecycle = "permanent";
      bird.expiresAt = null;
      bird.promotedAt ??= now2;
      this.collect(state, bird.speciesId, now2);
      return snapshotOf(state, now2);
    });
  }
  validName(name) {
    const trimmed = name.trim();
    if (trimmed.length > 60 || hasControlCharacters(trimmed))
      throw new YardError(
        "INVALID",
        "Choose a name of at most 60 characters without control characters."
      );
    return trimmed || null;
  }
  rename(ownerId, birdId, name, now2 = nowIso()) {
    now2 = normalizeNow(now2);
    return this.mutate(ownerId, (state) => {
      this.bird(state, birdId).name = this.validName(name);
      return snapshotOf(state, now2);
    });
  }
  /** Remove only this display instance; evidence, species collection and immutable assets survive. */
  removeBird(ownerId, birdId, now2 = nowIso()) {
    now2 = normalizeNow(now2);
    return this.mutate(ownerId, (state) => {
      this.bird(state, birdId);
      state.birds = state.birds.filter((bird) => bird.id !== birdId);
      return snapshotOf(state, now2);
    });
  }
  addInstance(ownerId, speciesId, name, now2 = nowIso()) {
    now2 = normalizeNow(now2);
    return this.mutate(ownerId, (state) => {
      this.collect(state, speciesId, now2);
      const artwork = state.artworks.filter((art) => art.speciesId === speciesId && this.selectableArtwork(ownerId, art, state)).sort((a2, b2) => b2.version - a2.version)[0];
      state.birds.push({
        id: randomUUID(),
        speciesId,
        name: name === void 0 ? null : this.validName(name),
        lifecycle: "permanent",
        createdAt: now2,
        promotedAt: now2,
        expiresAt: null,
        artworkId: artwork?.id ?? null,
        originEventId: null
      });
      return snapshotOf(state, now2);
    });
  }
  collectSpecies(ownerId, speciesId, now2 = nowIso()) {
    now2 = normalizeNow(now2);
    return this.mutate(ownerId, (state) => {
      this.collect(state, speciesId, now2);
      return snapshotOf(state, now2);
    });
  }
  updatePreferences(ownerId, patch, now2 = nowIso()) {
    now2 = normalizeNow(now2);
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
      return snapshotOf(state, now2);
    });
  }
  addObject(ownerId, kind, now2 = nowIso()) {
    now2 = normalizeNow(now2);
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
      return snapshotOf(state, now2);
    });
  }
  moveObject(ownerId, objectId, x, y, now2 = nowIso(), expected) {
    now2 = normalizeNow(now2);
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
      return snapshotOf(state, now2);
    });
  }
  removeObject(ownerId, objectId, now2 = nowIso()) {
    now2 = normalizeNow(now2);
    idSchema.parse(objectId);
    return this.mutate(ownerId, (state) => {
      if (!state.environment.objects.some((item) => item.id === objectId))
        throw new YardError("NOT_FOUND", "Object not found in this yard.");
      state.environment.objects = state.environment.objects.filter((item) => item.id !== objectId);
      return snapshotOf(state, now2);
    });
  }
  /** Exact retries retain their receipt even after later moves, returns or restores. */
  objectInventory(ownerId, input, now2 = nowIso()) {
    now2 = normalizeNow(now2);
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
        return snapshotOf(state, now2);
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
      return snapshotOf(state, now2);
    });
  }
  updateWeather(ownerId, settings, now2 = nowIso()) {
    now2 = normalizeNow(now2);
    const parsed = weatherSettingsSchema.parse(settings);
    return this.mutate(ownerId, (state) => {
      state.environment.weather = parsed;
      return snapshotOf(state, now2);
    });
  }
  registerArtwork(ownerId, input, now2 = nowIso()) {
    now2 = normalizeNow(now2);
    const art = artworkSchema.parse(input);
    return this.mutate(ownerId, (state) => {
      if (!state.species.some((s) => s.id === art.speciesId))
        throw new YardError("NOT_FOUND", "Artwork requires a known species.");
      if (state.artworks.some(
        (a2) => a2.id === art.id || a2.speciesId === art.speciesId && a2.version === art.version
      ))
        throw new YardError("CONFLICT", "Artwork is immutable; create a new ID and version.");
      state.artworks.push(art);
      for (const bird of state.birds)
        if (bird.speciesId === art.speciesId && !bird.artworkId && this.selectableArtwork(ownerId, art, state))
          bird.artworkId = art.id;
      return snapshotOf(state, now2);
    });
  }
  /** Explicit per-resident selection; never auto-pins siblings or mutates previous art. */
  pinAnimation(ownerId, birdId, input, now2 = nowIso()) {
    now2 = normalizeNow(now2);
    return this.mutate(ownerId, (state) => {
      const bird = this.bird(state, birdId);
      if (bird.speciesId !== input.speciesId)
        throw new YardError("INVALID", "Animation species does not match this bird.");
      const art = artworkSchema.parse({
        ...input,
        id: randomUUID(),
        version: 1 + Math.max(
          0,
          ...state.artworks.filter((a2) => a2.speciesId === bird.speciesId).map((a2) => a2.version)
        )
      });
      if (!art.animationPin) throw new YardError("INVALID", "An exact animation pin is required.");
      if (!this.selectableArtwork(ownerId, art, state))
        throw new YardError(
          "CONFLICT",
          "Restore this archived or unavailable asset dependency before selecting it."
        );
      const existing = state.artworks.find(
        (a2) => a2.speciesId === art.speciesId && JSON.stringify(a2.animationPin) === JSON.stringify(art.animationPin)
      );
      if (!existing) state.artworks.push(art);
      bird.artworkId = existing?.id ?? art.id;
      return snapshotOf(state, now2);
    });
  }
  /** Lifecycle CAS; immutable artwork and evidence remain available for explicit undo. */
  pinCatalog(ownerId, birdId, expectedArtworkId, input, now2 = nowIso()) {
    now2 = normalizeNow(now2);
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
          ...state.artworks.filter((a2) => a2.speciesId === bird.speciesId).map((a2) => a2.version)
        )
      });
      if (!art.catalogPin || !this.selectableArtwork(ownerId, art, state))
        throw new YardError(
          "CONFLICT",
          "This shared catalog release is unavailable for selection."
        );
      const existing = state.artworks.find(
        (a2) => a2.speciesId === art.speciesId && a2.catalogPin && canonicalJson(a2.catalogPin) === canonicalJson(art.catalogPin) && this.selectableArtwork(ownerId, a2, state)
      );
      if (!existing) state.artworks.push(art);
      bird.artworkId = existing?.id ?? art.id;
      return snapshotOf(state, now2);
    });
  }
  /** Lifecycle CAS; immutable artwork and evidence remain available for explicit undo. */
  replaceArtworkSelection(ownerId, birdId, expected, next, now2 = nowIso()) {
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
      return snapshotOf(state, normalizeNow(now2));
    });
  }
  exportBackup(ownerId, now2 = nowIso()) {
    return backupSchema.parse({
      format: "chirpneighbors-yard",
      version: 2,
      exportedAt: normalizeNow(now2),
      data: this.read(ownerId)
    });
  }
  /** Explicit replacement of this owner's yard; supplied owner IDs are never accepted. */
  restoreBackup(ownerId, input, now2 = nowIso()) {
    now2 = normalizeNow(now2);
    checkOwner(ownerId);
    const data = external_exports.object({ version: external_exports.literal(1) }).safeParse(input).success ? migrateV1(input, now2) : backupSchema.parse(input).data;
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
      this.hooks.restored?.(ownerId, now2);
      return snapshotOf(data, now2);
    });
  }
  migrateV1(ownerId, input, now2 = nowIso()) {
    return this.restoreBackup(ownerId, input, now2);
  }
};

// ../audit-storage-concurrency-probe.ts
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { Worker } from "node:worker_threads";
import { randomUUID as randomUUID2 } from "node:crypto";
import { once } from "node:events";
var root = mkdtempSync(join(tmpdir(), "chirp-storage-audit-"));
var path = join(root, "synthetic.sqlite");
var a = new YardRepository(path);
var b = new YardRepository(path);
var now = "2026-10-12T12:00:00.000Z";
var report = { syntheticOnly: true, realOwnerData: false };
try {
  a.updatePreferences("synthetic:alice", { palette: "twilight" }, now);
  const worker = new Worker(`const {parentPort,workerData}=require('node:worker_threads');const {DatabaseSync}=require('node:sqlite');const db=new DatabaseSync(workerData);db.exec('PRAGMA busy_timeout=5000; BEGIN IMMEDIATE');db.prepare("UPDATE yard_owners SET data=json_set(data,'$.preferences.palette','moonlit') WHERE owner_id=?").run('synthetic:alice');parentPort.postMessage('locked');setTimeout(()=>{db.exec('COMMIT');db.close();parentPort.close()},300);`, { eval: true, workerData: path });
  await once(worker, "message");
  const readStart = performance.now();
  const whileLocked = b.snapshot("synthetic:alice", now);
  const readMs = performance.now() - readStart;
  const writeStart = performance.now();
  const after = a.updatePreferences("synthetic:alice", { reducedMotion: true }, now);
  const writeMs = performance.now() - writeStart;
  await once(worker, "exit");
  report.wal = { readMs, writeWaitMs: writeMs, readerSawCommittedPalette: whileLocked.preferences.palette, finalPalette: after.preferences.palette, finalReducedMotion: after.preferences.reducedMotion, preservedOtherWriter: after.preferences.palette === "moonlit" && after.preferences.reducedMotion };
  const before = a.snapshot("synthetic:alice", now);
  const expected = { scene: before.preferences.scene, scenePin: before.preferences.scenePin, objects: before.environment.objects };
  const request = { action: "object-inventory", requestId: randomUUID2(), expected, payload: { operation: "return", objectId: before.environment.objects[0].id } };
  const committed = b.objectInventory("synthetic:alice", request, now);
  let staleCode = null;
  try {
    a.objectInventory("synthetic:alice", { ...request, requestId: randomUUID2() }, now);
  } catch (error) {
    staleCode = error.code;
  }
  const retried = a.objectInventory("synthetic:alice", request, now);
  let changedRetryCode = null;
  try {
    a.objectInventory("synthetic:alice", { ...request, payload: { operation: "return", objectId: before.environment.objects[1].id } }, now);
  } catch (error) {
    changedRetryCode = error.code;
  }
  report.cas = { staleCode, changedRetryCode, exactRetryPreserved: JSON.stringify(retried) === JSON.stringify(committed), receiptCount: retried.environment.objectReceipts.length, otherOwnerReceiptCount: b.snapshot("synthetic:bob", now).environment.objectReceipts.length };
  report.journalMode = a.database.prepare("PRAGMA journal_mode").get();
  report.busyTimeout = a.database.prepare("PRAGMA busy_timeout").get();
} finally {
  a.close();
  b.close();
  rmSync(root, { recursive: true, force: true });
}
writeFileSync("/workspace/archive-history/audit-storage-concurrency-results.json", JSON.stringify(report, null, 2) + "\n");
console.log(JSON.stringify(report, null, 2));
