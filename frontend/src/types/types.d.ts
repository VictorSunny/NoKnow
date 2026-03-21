type simpleContextState = {
  text: string;
  value: string | number;
};

type Children = React.ReactNode;

type SingleChildrenProp = {
  children?: Children;
};
type FormOnSubmitProps = {
  onSubmit: FormEventHandler<HTMLFormElement>;
};

export type OTPType = "email_change" | "password_change" | "signup" | "login";

type SortOrder = "asc" | "desc";
type FromDate = "all" | "1d" | "7d" | "1m" | "3m" | "6m" | "1y";

type Validity = "all" | "fresh" | "expired";

type OptionalBooleanString = "true" | "false" | "all";

type SortByDateOrID = "date" | "id";

type APIModelName = "chatroom" | "user" | "blacklistedEmail" | "blacklistedToken";

type OptionDict<T> = { value: T; text: string };
type KeyText<T> = Record<T, string>;

type SetBoolState = React.Dispatch<React.SetStateAction<boolean>>;

type SetOptionalTextState = React.Dispatch<SetStateAction<string | undefined>>;
