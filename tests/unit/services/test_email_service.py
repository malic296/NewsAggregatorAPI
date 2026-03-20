import resend

def test_send_email(mocker, email_service):
    send_mock = mocker.patch.object(resend.Emails, "send")
    code = 123456
    receiver = "delivered@resend.com"
    email_service.send_verification_code(email=receiver, code=code)

    send_mock.assert_called_once()

    args = send_mock.call_args.args[0]

    assert args["to"] == [receiver]
    assert args["from"] == "FedUp <onboarding@contact.fedup.live>"
    assert args["subject"] == "FedUp - Your Email Verification Code"
    assert str(code) in args["html"]