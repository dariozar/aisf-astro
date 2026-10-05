import { defineCollection, z } from "astro:content";
import { glob, file } from "astro/loaders";

const events = defineCollection({
  loader: glob({ base: "./src/content/events", pattern: "**/*.md" }),
  schema: z.object({
    id: z.string(),
    title: z.string(),
    date: z.string(),
    dateISO: z.string().optional().default(""),
    endDate: z.string().optional().default(""),
    location: z.string().optional().default(""),
    type: z.string().optional().default("evento"),
    cover: z.string().optional().default(""),
    status: z.enum(["upcoming", "past"]).default("past"),
  }),
});

const news = defineCollection({
  loader: glob({ base: "./src/content/news", pattern: "**/*.md" }),
  schema: z.object({
    title: z.string(),
    date: z.string(),
  }),
});

const committees = defineCollection({
  loader: file("src/data/committees.yml"),
  schema: z.object({
    id: z.string(),
    name: z.string(),
    president: z.string().optional().default(""),
    founded: z.string().optional().default(""),
    email: z.string().optional().default(""),
    status: z.string().optional().default("active"),
    photo: z.string().optional().default(""),
    logo: z.string().optional().default(""),
    past_presidents: z.string().optional().default(""),
    link: z.string().optional().default(""),
    rules: z.string().optional().default(""),
  }),
});

const executive = defineCollection({
  loader: file("src/data/executive.yml"),
  schema: z.object({
    id: z.string(),
    name: z.string(),
    role: z.string(),
    bio: z.string().optional().default(""),
    email: z.string().optional().default(""),
    photo: z.string().optional().default(""),
  }),
});

const documents = defineCollection({
  loader: file("src/data/documents.yml"),
  schema: z.object({
    id: z.string(),
    year: z.string(),
    group: z.string(),
    name: z.string(),
    url: z.string(),
  }),
});

const executivePast = defineCollection({
  loader: file("src/data/executive-past.yml"),
  schema: z.object({
    id: z.string(),
    mandate: z.string(),
    members: z.array(z.object({ name: z.string(), role: z.string() })),
  }),
});

export const collections = { events, news, committees, executive, executivePast, documents };
