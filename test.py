import logging
import elks

logging.getLogger().setLevel(logging.INFO)

def main():
    username = '<Your 46elks API username>'
    password = '<Your 46elks API password>'

    elk = elks.API(username, password)
    number = elk.allocateNumber()
    logging.info('Allocated number: %s' % number))

    number.modify(sms_callback_url='http://example.com/sms_cb')

    sms = number.sendMessage(to='+46123456789', message='Hello world')
    logging.info('Sent message "%s" to "%s"' % (sms.message, sms.receiver))

if __name__ == "__main__":
    main()
