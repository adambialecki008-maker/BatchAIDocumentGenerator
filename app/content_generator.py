from app.models import ClientInput, GeneratedContent


class FakeGenerator:
    def generate(self, client: ClientInput) -> GeneratedContent:
        return GeneratedContent(
            professional_summary=(
                f"{client.first_name} {client.last_name} is an experienced"
                f"{client.target_role}"
            ),
            key_strengths=(
                client.skills,
                client.key_achievement,
            ),
            cover_letter_body=(
                f"I am intereseted in {client.target_role} position"
                f"at {client.target_company}"
            ),
        )
