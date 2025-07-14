.runs[]?.tool |
  (.driver.rules[]?, .extensions[]?.rules[]?) |= (
    .shortDescription |= (. // {} | {"text": ""} + .) |
    .fullDescription |= (. // {} | {"text": ""} + .)
  )