import { FromDate, KeyText, OptionalBooleanString, SortByDateOrID, SortOrder, Validity } from "../types/types";

export const sortOrderOptions: SortOrder[] = ["asc", "desc"];
export const FromDateOptions: FromDate[] = ["all", "1d", "7d", "1m", "3m", "6m", "1y"];
export const optionalBooleanOptions: OptionalBooleanString[] = ["all", "true", "false"];
export const sortByDateOrIDOptions: SortByDateOrID[] = ["date", "id"]
export const validityOptions: Validity[] = ["all", "fresh", "expired"]

export const sortOrderTexts: KeyText<SortOrder> = {
  asc: "ascending",
  desc: "descending",
};
export const fromDateTexts: KeyText<FromDate> = {
  all: "all time",
  "1d": "past day",
  "7d": "past week",
  "1m": "past month",
  "3m": "past 3 months",
  "6m": "past 6 months",
  "1y": "past year",
};

export const optionalBooleanTexts: KeyText<OptionalBooleanString> = {
  all: "all",
  true: "yes",
  false: "no",
};

export const sortByDateOrIDTexts: KeyText<SortByDateOrID> = {
  "id": "index",
  "date": "date created",
}

export const validityTexts: KeyText<Validity> = {
  "all": "all",
  "fresh": "fresh",
  "expired": "expired", 
}
