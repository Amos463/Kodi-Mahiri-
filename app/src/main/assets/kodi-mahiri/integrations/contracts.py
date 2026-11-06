"""Mikataba ya adapter ili kuunganisha watoa huduma bila kubadilisha tax engine."""
from abc import ABC, abstractmethod

class USSDGateway(ABC):
    @abstractmethod
    def send_response(self, session_id: str, text: str, end: bool = False): ...

class SMSGateway(ABC):
    @abstractmethod
    def send_sms(self, recipient: str, message: str): ...

class IVRGateway(ABC):
    @abstractmethod
    def play_prompt(self, call_id: str, text: str): ...

class BusinessTransactionProvider(ABC):
    @abstractmethod
    def fetch_transactions(self, business_number: str, start, end): ...

class TaxAuthorityProvider(ABC):
    @abstractmethod
    def submit_assessment(self, approved_payload: dict): ...
    @abstractmethod
    def verify_taxpayer(self, tin: str): ...

class PaymentProvider(ABC):
    @abstractmethod
    def create_official_control_number(self, approved_assessment_id: str): ...
    @abstractmethod
    def verify_payment(self, provider_reference: str): ...
