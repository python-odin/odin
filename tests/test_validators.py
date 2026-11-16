import pytest

from odin import validators
from odin.exceptions import ValidationError


class TestRegexValidator:
    def test_regex_validator__with_valid_values(self):
        # Arrange
        target = validators.RegexValidator(
            r"^[a-z]{3}$", "Please enter 3 alpha characters.", "match_chars"
        )

        # Assert initial attributes
        assert target.message == "Please enter 3 alpha characters."
        assert target.code == "match_chars"

        # Act & Assert - valid
        target("abc")
        target("cba")

    def test_regex_validator__with_invalid_values(self):
        # Arrange
        target = validators.RegexValidator(
            r"^[a-z]{3}$", "Please enter 3 alpha characters.", "match_chars"
        )

        # Act & Assert - invalid
        with pytest.raises(ValidationError):
            target("a")
        with pytest.raises(ValidationError):
            target("abcd")
        with pytest.raises(ValidationError):
            target("123")

    def test_regex_validator__with_non_string_value(self):
        # Arrange
        target = validators.RegexValidator(r"^[0-9]+$")

        # Act & Assert
        with pytest.raises(ValidationError):
            target(123)
        with pytest.raises(ValidationError):
            target(None)

    def test_regex_validator__with_inverse_match(self):
        # Arrange
        target = validators.RegexValidator(r"^[0-9]+$", inverse_match=True)

        # Act & Assert - non-matching strings pass
        target("abc")
        target("hello world")

        # Act & Assert - matching strings fail
        with pytest.raises(ValidationError):
            target("12345")

    def test_regex_validator__string_representation(self):
        # Arrange
        target = validators.RegexValidator(r"^[a-z]+$")

        # Act
        result = str(target)

        # Assert
        assert result == "RegexValidator(^[a-z]+$)"

    def test_regex_validator__custom_description(self):
        # Arrange
        target = validators.RegexValidator(
            r"^[a-z]+$", description="Only lowercase characters."
        )

        # Act
        result = str(target)

        # Assert
        assert result == "Only lowercase characters."


class TestURLValidator:
    @pytest.mark.parametrize(
        "value",
        (
            "http://www.djangoproject.com/",
            "http://localhost/",
            "http://example.com/",
            "http://www.example.com/",
            "http://www.example.com:8000/test",
            "http://valid-with-hyphens.com/",
            "http://subdomain.example.com/",
            "http://200.8.9.10/",
            "http://200.8.9.10:8000/test",
            "http://valid-----hyphens.com/",
            "http://example.com?something=value",
            "http://example.com/index.php?something=value&another=value2",
            "https://example.com/",
            "ftp://example.com/",
            "ftps://example.com/",
            "http://savage.company/",
        ),
    )
    def test_validate_url__where_value_is_valid(self, value):
        # Arrange & Act & Assert
        validators.validate_url(value)

    @pytest.mark.parametrize(
        "value",
        (
            "foo",
            "http://",
            "http://example",
            "http://example.",
            "http://.com",
            "http://invalid-.com",
            "http://-invalid.com",
            "http://inv-.alid-.com",
            "http://inv-.-alid.com",
        ),
    )
    def test_validate_url__where_value_is_not_valid(self, value):
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            validators.validate_url(value)

    def test_validate_url__string_representation(self):
        # Arrange & Act
        result = str(validators.validate_url)

        # Assert
        assert result == "Value is a valid URL."


class TestNumericAndLengthValidators:
    def test_max_value_validator(self):
        # Arrange
        target = validators.MaxValueValidator(10)

        # Act & Assert
        target(10)
        target(1)
        target(-10)
        assert str(target) == "Value is less than or equal to 10."
        with pytest.raises(ValidationError):
            target(11)

    def test_min_value_validator(self):
        # Arrange
        target = validators.MinValueValidator(10)

        # Act & Assert
        target(10)
        target(11)
        assert str(target) == "Value is greater than or equal to 10."
        with pytest.raises(ValidationError):
            target(1)
        with pytest.raises(ValidationError):
            target(-10)

    def test_between_validator__within_bounds(self):
        # Arrange
        target = validators.BetweenValidator(5, 10)

        # Act & Assert
        target(5)
        target(7)
        target(10)
        assert str(target) == "Value is between 5 and 10."

    def test_between_validator__outside_bounds(self):
        # Arrange
        target = validators.BetweenValidator(5, 10)

        # Act & Assert
        with pytest.raises(ValidationError):
            target(4)
        with pytest.raises(ValidationError):
            target(11)

    def test_length_validator(self):
        # Arrange
        target = validators.LengthValidator(10)

        # Act & Assert
        target("1234567890")
        assert str(target) == "Value's length is 10."
        with pytest.raises(ValidationError):
            target("123456789")
        with pytest.raises(ValidationError):
            target("12345678901")

    def test_max_length_validator(self):
        # Arrange
        target = validators.MaxLengthValidator(10)

        # Act & Assert
        target("123457890")
        target("12345")
        target("")
        assert str(target) == "Value's length is at most 10."
        with pytest.raises(ValidationError):
            target("12345678901")

    def test_min_length_validator(self):
        # Arrange
        target = validators.MinLengthValidator(10)

        # Act & Assert
        target("12345678901")
        assert str(target) == "Value's length is at least 10."
        with pytest.raises(ValidationError):
            target("123457890")
        with pytest.raises(ValidationError):
            target("12345")
        with pytest.raises(ValidationError):
            target("")

    def test_validator_slots_defined(self):
        # Arrange & Act & Assert
        for cls in (
            validators.MaxValueValidator,
            validators.MinValueValidator,
            validators.LengthValidator,
            validators.MaxLengthValidator,
            validators.MinLengthValidator,
        ):
            instance = cls(10)
            assert not hasattr(instance, "__dict__")


class TestSimpleValidator:
    def test_method(self):
        # Arrange
        def reflect(v):
            return v

        validator = validators.simple_validator(reflect)

        # Act & Assert
        validator(True)
        with pytest.raises(ValidationError):
            validator(False)

    def test_decorator(self):
        # Arrange
        @validators.simple_validator()
        def reflect_validator(v):
            return v

        # Act & Assert
        reflect_validator(True)
        with pytest.raises(ValidationError):
            reflect_validator(False)

    def test_str__description(self):
        # Arrange
        @validators.simple_validator(description="Mirror Validator")
        def reflect_validator(v):
            return v

        # Act & Assert
        assert str(reflect_validator) == "Mirror Validator"

    def test_str__no_doc_text(self):
        # Arrange
        @validators.simple_validator()
        def reflect_validator(v):
            return v

        # Act & Assert
        assert str(reflect_validator) == "reflect_validator"

    def test_str__doc_text(self):
        # Arrange
        @validators.simple_validator()
        def reflect_validator(v):
            """Reflect Validator"""
            return v

        # Act & Assert
        assert str(reflect_validator) == "Reflect Validator"


class TestIPValidators:
    @pytest.mark.parametrize(
        "value",
        (
            "192.168.0.1",
            "1.1.1.1",
            "255.255.255.255",
        ),
    )
    def test_ipv4_address_valid(self, value):
        # Arrange & Act & Assert
        validators.validate_ipv4_address(value)

    @pytest.mark.parametrize(
        "value",
        (
            ".2.3.4",
            "1.2.3",
            "1.2.3.4.5",
            "300.0.0.1",
            "ff.ff.ff.ff",
            "abcd",
            "",
            "::ff:ff:ff:ff",
        ),
    )
    def test_ipv4_address_invalid(self, value):
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            validators.validate_ipv4_address(value)

    def test_ipv4_address_str(self):
        # Arrange & Act
        result = str(validators.validate_ipv4_address)

        # Assert
        assert result == "Value is an IPv4 Address."

    def test_ipv4_address_custom_init(self):
        # Arrange
        validator = validators.IPv4Address(
            message="Invalid IPv4",
            code="bad_ipv4",
            description="Custom IPv4 Validator",
        )

        # Act & Assert
        assert str(validator) == "Custom IPv4 Validator"
        with pytest.raises(ValidationError) as exc_info:
            validator("invalid_ip")
        assert exc_info.value.code == "bad_ipv4"
        assert exc_info.value.messages == ["Invalid IPv4"]

    @pytest.mark.parametrize(
        "value",
        (
            "::",  # Localhost
            "::1",  # Default unicast
            "::ffff:0:0",  # IPv4 Mapped address
            "2002::",  # 6to4
            "2001::",  # Teredo tunneling
            "fc00::",  # Unique local address
            "ffff::192.168.0.1",
            "1:2:3:4:5:6:7:8",
            "dead:beef:dead:beef:dead:beef:dead:beef",
        ),
    )
    def test_ipv6_address_valid(self, value):
        # Arrange & Act & Assert
        validators.validate_ipv6_address(value)

    @pytest.mark.parametrize(
        "value",
        (
            "192.168.0.1",
            "1:2:3:4:5:6:7:8:9",
            "1234:5678:9abc:defg::",
            "2001::12345",
            "::ffff::",
            "ff:::0",
            ":2:3:4:5:6:7:8",
            "1:2:3:4:5:6:7:",
            ":2:3:4:5:6:7:",
            "1:2:3:4:5:192.168.0",
            "1:2:3:4:256.256.256.256",
            "192.168.0.1::ff",
            "zzzz::0",
        ),
    )
    def test_ipv6_address_invalid(self, value):
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            validators.validate_ipv6_address(value)

    @pytest.mark.parametrize(
        "value",
        (
            "192.168.0.1",
            "1:2:3:4:5:6:7:8",
        ),
    )
    def test_validate_ipv46_address_valid(self, value):
        # Arrange & Act & Assert
        validators.validate_ipv46_address(value)

    @pytest.mark.parametrize(
        "value",
        (
            "192.168.0.",
            "1:2:3:4:5:6:7:8:9",
        ),
    )
    def test_validate_ipv46_address_invalid(self, value):
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            validators.validate_ipv46_address(value)


class TestEmailValidator:
    @pytest.mark.parametrize(
        "value,kwargs",
        (
            ("foo@bar.com", None),
            ("FOO@BAR.COM", None),
            ("foo@localhost", None),
            # New release domain names
            ("foo@example.company", None),
            # IPv4 based email
            ("foo@[127.0.0.1]", None),
            # IPv6 based email
            ("foo@[::1]", None),
        ),
    )
    def test_validate_email_valid(self, value, kwargs):
        # Arrange
        kwargs = kwargs or {}
        validator = validators.EmailValidator(**kwargs)

        # Act & Assert
        validator(value)

    @pytest.mark.parametrize(
        "value,kwargs",
        (
            ("foo", None),
            (".foo@bar.com", None),
            ("foo@corpau", None),
            ("foo@localhost", {"whitelist": ""}),
            ("foo@{}.com".format("a" * 64), None),
            ("foo@[::ff::0]", None),
            # RFC 5321 length limits
            ("a" * 65 + "@example.com", None),  # user part > 64
            ("foo@" + "a" * 256 + ".com", None),  # domain part > 255
            ("a" * 245 + "@example.com", None),  # total len > 254
            (12345, None),  # non-string
            (None, None),  # none
        ),
    )
    def test_validate_email_invalid(self, value, kwargs):
        # Arrange
        kwargs = kwargs or {}
        validator = validators.EmailValidator(**kwargs)

        # Act & Assert
        with pytest.raises(ValidationError):
            validator(value)

    def test_validate_email_str(self):
        # Arrange & Act
        result = str(validators.validate_email_address)

        # Assert
        assert result == "Value is a valid Email address."
