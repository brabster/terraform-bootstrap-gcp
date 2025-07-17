Ask me any questions that are needed to refine my intent.

Generate a prompt template file.
The template will be provided to an AI agent along with a prompt outlining a specific feature or fix.
The AI agent will use the template to generate a meta-prompt for the agent's subsequent implementation of the feature or fix.

The tempate should begin with a frontmatter in YAML format, and template consumers should provide a `prompt` key with the original prompt they were given, and a `refinement` key, containing a summary of any conversational refinement that followed.

The template should have a structure that is optimised for an LLM to use as system context, yet also human readable.

It should ensure that the LLM asks questions to clarify intent and context, and that it takes step to validate that the feature works correctly.

It should ensure that the LLM performs a pre-mortem and highlights any potential showstoppers and external dependencies that might cause problems for implementation.

Have the template end with a section to reference important sources, then close with a TL;DR section at the end of the rules template!

The template should be short and concise (under 200 lines), but ensure that important topics are covered.
Follow industry best practices and emerging patterns found on the internet for meta-prompting and specification-driven development when formulating this rules template!

Write the template to the prompts/features directory as 00-feature-template.md.