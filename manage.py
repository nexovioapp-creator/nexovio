#!/usr/bin/env python
import os, sys

# python manage.py makemigrations
# python manage.py migrate
# python manage.py shell
# python manage.py runserver
# & "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://localhost:8000

# to fix fields
# python manage.py fix_mobile_fields

# to load db
# python manage.py load_mobiles --file mobiles_final.csv
# python manage.py load_mobile_prices mobile_price_final.csv

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobile_price_compare.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
if __name__ == '__main__':
    main()
