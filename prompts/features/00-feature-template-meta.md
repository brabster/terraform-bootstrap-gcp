Generate a file template that I can base a unit of work like a feature or a fix on.

Start the template with YAML frontmatter including the prompt that was used, verbatim.

The rules template should have a structure that is optimised for an LLM to use as system context, yet also human readable. It should ensure that the LLM asks questions to clarify intent and context. It should ensure that the LLM performs a pre-mortem and discusses any potential showstoppers with the human user.

The target rules should generally stay short and concise (under 200 lines)

Have the template end with a section to reference important sources, then close with a TL;DR section at the end of the rules template!

Follow industry best practices and emerging patterns found on the internet for rules files when formulating this rules template!

Write the rules template to the prompts/features directory as 00-feature-template.md.