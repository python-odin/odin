import pytest

from odin import validators
from odin.exceptions import ValidationError


class TestValidator:
    def test_regex_validator__with_valid_values(self):
        target = validators.RegexValidator(
            r"^[a-z]{3}$", "Please enter 3 alpha characters.", "match_chars"
        )

        assert "Please enter 3 alpha characters." == target.message
        assert "match_chars" == target.code

        target("abc")
        target("cba")
        pytest.raises(ValidationError, target, "a")
        pytest.raises(ValidationError, target, "abcd")
        pytest.raises(ValidationError, target, "123")

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
        with pytest.raises(ValidationError):
            validators.validate_url(value)

    def test_validate_url__string_representation(self):
        assert str(validators.validate_url) == "Value is a valid URL."

    def test_max_value_validator(self):
        target = validators.MaxValueValidator(10)

        target(10)
        target(1)
        target(-10)
        assert str(target) == "Value is less than or equal to 10."
        pytest.raises(ValidationError, target, 11)

    def test_min_value_validator(self):
        target = validators.MinValueValidator(10)

        target(10)
        target(11)
        assert str(target) == "Value is greater than or equal to 10."
        pytest.raises(ValidationError, target, 1)
        pytest.raises(ValidationError, target, -10)

    def test_length_validator(self):
        target = validators.LengthValidator(10)

        target("1234567890")
        assert str(target) == "Values length is 10."
        pytest.raises(ValidationError, target, "123456789")
        pytest.raises(ValidationError, target, "12345678901")

    def test_max_length_validator(self):
        target = validators.MaxLengthValidator(10)

        target("123457890")
        target("12345")
        target("")
        assert str(target) == "Values length is at most 10."
        pytest.raises(ValidationError, target, "12345678901")

    def test_min_length_validator(self):
        target = validators.MinLengthValidator(10)

        target("12345678901")
        assert str(target) == "Values length is at least 10."
        pytest.raises(ValidationError, target, "123457890")
        pytest.raises(ValidationError, target, "12345")
        pytest.raises(ValidationError, target, "")


class TestSimpleValidator:
    def test_method(self):
        def reflect(v):
            return v

        validator = validators.simple_validator(reflect)

        pytest.raises(ValidationError, validator, False)
        validator(True)

    def test_decorator(self):
        @validators.simple_validator()
        def reflect_validator(v):
            return v

        pytest.raises(ValidationError, reflect_validator, False)
        reflect_validator(True)

    def test_str__description(self):
        @validators.simple_validator(description="Mirror Validator")
        def reflect_validator(v):
            return v

        assert str(reflect_validator) == "Mirror Validator"

    def test_str__no_doc_text(self):
        @validators.simple_validator()
        def reflect_validator(v):
            return v

        assert str(reflect_validator) == "reflect_validator"

    def test_str__doc_text(self):
        @validators.simple_validator()
        def reflect_validator(v):
            """
            Reflect Validator
            """
            return v

        assert str(reflect_validator) == "Reflect Validator"


@pytest.mark.parametrize(
    "value",
    (
        "192.168.0.1",
        "1.1.1.1",
        "255.255.255.255",
    ),
)
def test_ipv4_address_valid(value):
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
def test_ipv4_address_invalid(value):
    with pytest.raises(ValidationError):
        validators.validate_ipv4_address(value)


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
def test_ipv6_address_valid(value):
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
def test_ipv6_address_invalid(value):
    with pytest.raises(ValidationError):
        validators.validate_ipv6_address(value)


@pytest.mark.parametrize(
    "value",
    (
        "192.168.0.1",
        "1:2:3:4:5:6:7:8",
    ),
)
def test_validate_ipv46_address_valid(value):
    validators.validate_ipv46_address(value)


@pytest.mark.parametrize(
    "value",
    (
        "192.168.0.",
        "1:2:3:4:5:6:7:8:9",
    ),
)
def test_validate_ipv46_address_invalid(value):
    with pytest.raises(ValidationError):
        validators.validate_ipv46_address(value)


@pytest.mark.parametrize(
    "value kwargs".split(),
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
def test_validate_email_valid(value, kwargs):
    kwargs = kwargs or {}
    validators.EmailValidator(**kwargs)(value)


@pytest.mark.parametrize(
    "value kwargs".split(),
    (
        ("foo", None),
        (".foo@bar.com", None),
        ("foo@corpau", None),
        ("foo@localhost", {"whitelist": ""}),
        ("foo@{}.com".format("a" * 64), None),
        ("foo@[::ff::0]", None),
    ),
)
def test_validate_email_invalid(value, kwargs):
    kwargs = kwargs or {}
    with pytest.raises(ValidationError):
        validators.EmailValidator(**kwargs)(value)
