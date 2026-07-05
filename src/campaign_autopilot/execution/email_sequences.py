"""Email Sequences — backward-compat shim."""
from .scheduler import EmailSequenceEngine, DripCampaign, WELCOME_SEQUENCE, AFFILIATE_SEQUENCE
__all__ = ["EmailSequenceEngine", "DripCampaign", "WELCOME_SEQUENCE", "AFFILIATE_SEQUENCE"]
