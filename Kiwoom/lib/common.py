def changeFormat(self, data, percent=0):
    if percent == 0:
        d = int(data)
        formatData = '{:-,d}'.format(d)

    elif percent == 1:
        f = int(data) / 100
        formatData = '{:-,.2f}'.format(f)

    elif percent == 2:
        f = float(data)
        formatData = '{:-,.2f}'.format(f)

    return formatData

@staticmethod
def change_format(data):
    strip_data = data.lstrip('-0')
    if strip_data == '':
        strip_data = '0'

    try:
        format_data = format(int(strip_data), ',d')
    except:
        format_data = format(float(strip_data))
    if data.startswith('-'):
        format_data = '-' + format_data

    return format_data


@staticmethod
def change_format2(data):
    strip_data = data.lstrip('-0')

    if strip_data == '':
        strip_data = '0'

    if strip_data.startswith('.'):
        strip_data = '0' + strip_data

    if data.startswith('-'):
        strip_data = '-' + strip_data

    return strip_data