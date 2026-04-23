import resend


def test_send_email(mocker, email_service):
    send_mock = mocker.patch.object(resend.Emails, "send")

    email_service.send_verification_code(email="user@example.com", code=123456)

    send_mock.assert_called_once()
    args = send_mock.call_args.args[0]
    assert args["to"] == ["user@example.com"]
    assert args["from"] == "FedUp <onboarding@contact.fedup.live>"
    assert args["subject"] == "FedUp - Your Email Verification Code"
    assert "123456" in args["html"]
