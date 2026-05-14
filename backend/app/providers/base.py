from typing import Protocol


class TextGenerationProvider(Protocol):
    def generate(self, prompt: str) -> dict: ...


class ImageGenerationProvider(Protocol):
    def generate(self, prompt: str) -> dict: ...

    def generate_texture(self, prompt: str, size: str, style_preset: str, scene_preset: str) -> dict: ...


class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> dict: ...
