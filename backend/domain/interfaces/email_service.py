
from typing import Protocol


# Interface definition using Protocol
class EmailServiceInterface(Protocol):
    async def send_email(self, to: str, subject: str, html_body: str) -> bool:
        ...
    
    async def send_verification_email(self, username: str, email: str, token: str) -> bool:
        ...
    
    async def send_password_reset_email(self, username: str, email: str, token: str) -> bool:
        ...