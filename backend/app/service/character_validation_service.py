from app.schema.analysis import CharacterValidationResult


def validate_character(character: str) -> CharacterValidationResult:
    normalized = character.strip()

    if len(normalized) != 1:
        return CharacterValidationResult(character=normalized, validated=False, message="请输入 1 个汉字。")

    return CharacterValidationResult(character=normalized, validated=True, message="ok")
