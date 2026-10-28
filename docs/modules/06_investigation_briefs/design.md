# Investigation brief design

An investigation-brief service builds a constrained JSON evidence payload from one alert and its linked records. A Gemini client receives only the required public data and returns a structured response validated by Pydantic.

Persist `pending`, `generated`, and `failed` brief states. Validate returned numerical claims against the evidence payload before marking a brief generated.
