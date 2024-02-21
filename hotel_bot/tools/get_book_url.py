import datetime


def get_book_url(arguments):
    """
    Returns a booking.com URL
    """
    # Extracting information from arguments
    guests = arguments.get('guests')
    checkin = arguments.get('checkin')
    checkout = arguments.get('checkout')

    _in = '2024-03-23'
    _out = '2024-09-29'
    checkin_starts = datetime.datetime.strptime(_in, '%Y-%m-%d').date()
    checkout_finish = datetime.datetime.strptime(_out, '%Y-%m-%d').date()

    # Validating the presence of all required information
    if not guests:
        return 'Missing required information. Please provide number of adult guests'
    if not checkin:
        return 'Missing required information. Please provide checkin date'
    if not checkout:
        return 'Missing required information. Please provide checkout date'
    try:
        checkin_date = datetime.datetime.strptime(checkin, '%Y-%m-%d').date()
        checkout_date = datetime.datetime.strptime(checkout, '%Y-%m-%d').date()
    except ValueError:
        return "Invalid date or time format. Please use 'YYYY-MM-DD' for date"

    # Check if the date in a good range
    if checkin_date < checkin_starts:
        return f'Hotel booking starts from {_in}. Please choose a another date.'
    if checkout_date > checkout_finish:
        return f'Hotel booking ends {_out}. Please choose a another date.'

    booking_url = f'https://www.booking.com/hotel/es/loft-hostal-group.en-gb.html?aid=304142&label=gen173nr-1FCAsoRkIRbG9mdC1ob3N0YWwtZ3JvdXBICVgEaEaIAQGYAQm4ARnIAQzYAQHoAQH4AQKIAgGoAgO4AvOJkK4GwAIB0gIkMjk0ZjVlMzEtMTM3Yi00ZjBjLWFmMmYtYjM1NWViYzliZmU02AIF4AIB&sid=8433218054fc210a56363ecc9f3631f2&checkin={checkin};checkout={checkout};dest_id=-389487;dest_type=city;dist=0;group_adults={guests};group_children=0;hapos=1;hpos=1;no_rooms=1;sb_price_type=total;soh=1;sr_order=popularity;srepoch=1708033291;srpvid=1a21985eef5a0039;type=total;ucfs=1'
    hostelworld_url = f'https://www.hostelworld.com/pwa/hosteldetails.php/Loft-Hostal/Lloret-de-Mar/286415?from={checkin}&to={checkout}&guests={guests}'
    # Checkin from 23 march to 29 september
    return f'Here is your URL for booking:\nHostelWorld - {hostelworld_url}\nBooking.com - {booking_url}'
    # return f'Here is your URL for booking https://www.booking.com/hotel/es/loft-hostal-group.en-gb.html?aid=304142&label=gen173nr-1FCAsoRkIRbG9mdC1ob3N0YWwtZ3JvdXBICVgEaEaIAQGYAQm4ARnIAQzYAQHoAQH4AQKIAgGoAgO4AvOJkK4GwAIB0gIkMjk0ZjVlZTMxMTM3Yi00ZjBjLWFmMmYtYjM1NWViYzliZmU02AIF4AIB&sid=8433218054fc210a56363ecc9f3631f2&checkin={checkin}&checkout={checkout}&dest_id=-389487&dest_type=city&dist=0&group_adults={guests}&group_children=0&hp_avform=1&hp_group_set=0&no_rooms=1&origin=hp&sb_price_type=total&src=hotel&type=total&#group_recommendation'
