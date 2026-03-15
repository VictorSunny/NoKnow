import slugify from "slugify";

export default function slugifyString(stringToParse: string) {
  const slug = slugify(stringToParse, {
    lower: true,
    strict: true,
  });
  return slug;
}
