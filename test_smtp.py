import smtplib
try:
    server = smtplib.SMTP_SSL('outgoing.workd.go.th', 465)
    server.set_debuglevel(1)
    server.login('learn2earn@bde.go.th', 'L2E@Start2026!')
    print('SUCCESS')
    server.quit()
except Exception as e:
    print('ERROR:', e)
