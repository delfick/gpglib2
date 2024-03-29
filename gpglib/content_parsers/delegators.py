from gpglib.content_parsers.base import Parser
from gpglib.content_parsers.data import (
    CompressedParser,
    LiteralParser,
    ModificationDetectionCodePacketParser,
    SymEncryptedParser,
    SymmetricallyEncryptedIntegrityProtectedDataPacketParser,
    UserIdParser,
)
from gpglib.content_parsers.keys import (
    PublicKeyParser,
    PublicSubKeyParser,
    SecretKeyParser,
    SecretSubKeyParser,
    SignatureParser,
)
from gpglib.content_parsers.session_keys import PubSessionKeyParser

####################
### DELEGATORS
####################


class ContentParser(object):
    """Delegator to the different content parsers"""

    def __init__(self):
        self.parsers = {}
        self.parse_unknown = self.parser_for_unknown()

        # Instantiate parsers from find_parsers
        # It is recommended that this instance of ContentParser is memoized when created
        for tag_type, kls in self.find_parsers():
            self.parsers[tag_type] = kls()

    def parser_for_unknown(self):
        """Return instantiated parser to handle unknown tags"""
        return Parser()

    def find_parsers(self):
        """Specify lists of [(tag_type, kls), (tag_type, kls), ...] for kls to handle each tag type"""
        raise NotImplementedError()

    def consume(self, tag, message, kwargs):
        """
        Find parser given tag.tag_type
        And consume the body of the tag using correct packet parser
        """
        # Determine what parser to use for this packet
        # Default to self.parse_unknown, which will do some complaining for us
        parser = self.parsers.get(tag.tag_type, self.parse_unknown)

        # Consume the desired region
        return parser.consume(tag, message, tag.body, **kwargs)


class PacketContentParser(ContentParser):
    def find_parsers(self):
        """Specifiy parsers"""
        return (
            (1, PubSessionKeyParser),
            (2, SignatureParser),
            (5, SecretKeyParser),
            (6, PublicKeyParser),
            (7, SecretSubKeyParser),
            (8, CompressedParser),
            (9, SymEncryptedParser),
            (11, LiteralParser),
            (13, UserIdParser),
            (14, PublicSubKeyParser),
            (18, SymmetricallyEncryptedIntegrityProtectedDataPacketParser),
            (19, ModificationDetectionCodePacketParser),
        )


class SubSignatureContentParser(ContentParser):
    def find_parsers(self):
        """Don't handle any sub signature packets yet"""
        return ()

    def parser_for_unknown(self):
        """Return instantiated parser to handle unknown tags"""

        def consume(parser, tag, message, region, subsignature=None):
            if not subsignature:
                subsignature = {}
            subsignature[tag.tag_type] = region.read("bytes")
            return {"subsignature": subsignature}

        return type("SignatureParser", (Parser,), {"consume": consume})()
