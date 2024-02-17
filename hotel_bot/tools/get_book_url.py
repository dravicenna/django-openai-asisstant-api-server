def get_book_url(arguments):
    """
    Returns a booking.com URL
    """
    # Extracting information from arguments
    guests = arguments.get('guests')
    checkin = arguments.get('checkin')
    checkout = arguments.get('checkout')

    # Validating the presence of all required information
    if not all([guests, checkin, checkout]):
        # TODO make different msg for each argument.
        return 'Missing required information. Please provide number of adult guests, checkin and checkout date.'
    # TODO check date here
    return f'Here is your URL for booking https://www.booking.com/hotel/es/loft-hostal-group.en-gb.html?aid=304142&label=gen173nr-1FCAsoRkIRbG9mdC1ob3N0YWwtZ3JvdXBICVgEaEaIAQGYAQm4ARnIAQzYAQHoAQH4AQKIAgGoAgO4AvOJkK4GwAIB0gIkMjk0ZjVlMzEtMTM3Yi00ZjBjLWFmMmYtYjM1NWViYzliZmU02AIF4AIB&sid=8433218054fc210a56363ecc9f3631f2&checkin={checkin};checkout={checkout};dest_id=-389487;dest_type=city;dist=0;group_adults={guests};group_children=0;hapos=1;hpos=1;no_rooms=1;req_adults={guests};req_children=0;room1=A%2CA%2CA;sb_price_type=total;soh=1;sr_order=popularity;srepoch=1708033291;srpvid=1a21985eef5a0039;type=total;ucfs=1&#no_availability_msg'
