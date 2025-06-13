csv_data = """Ad Id,Company Name,Location,Start Time,End Time,Description,Placement on Device,Rb/NRb,Availability
AD100,,Mumbai,,,"Pepsico ad at 9:30am for 30 mins",Top,Rb,Available
AD101,Cocacola,Kolkata,2025-06-11 12:00:00,,"Starts from noon, duration: 1hr",Bottom,Rb,Available
AD102,Nestle,Delhi,,,"Nestle showcasing at midnight for 45 mins",Full Screen,Rb,Available
AD103,HUL,Delhi,,,"Ad for HUL starts at 2pm and plays for 2 hours",Side Bar,NRb,Available
AD104,,"Hyderabad",,,"Company: Amul, plays at 10:15 for 1hr",Center,NRb,Available
AD105,Colgate,Delhi,2025-06-11 18:00:00,2025-06-11 19:00:00,Colgate dental ad,Top,Rb,Available
AD106,Lux,Mumbai,,,"Luxury soap ad by Lux, starts 6:30pm, runs 1.5 hrs",Bottom,Rb,Available
AD107,,Delhi,,,"Detol at 4:30pm for 90 mins",Side Bar,NRb,Available
AD108,Unilevr,Mumbai,2025-06-11 08:00:00,,"Unilevr early morning spot, 1 hr",Full Screen,Rb,Available
AD109,,Chennai,2025-06-11 13:00:00,,"Company is Garnier, ad runs for 1hr.",Top,NRb,Available
AD110,Pantene,Delhi,2025-06-11 20:00:00,2025-06-11 21:30:00,"Pantene Hairfall ad",Center,Rb,Available
AD111,,Delhi,,,"Clinic Plus, starts from 3 PM to 4:15 PM",Bottom,Rb,Available
AD112,Bisleri,Kolkata,,,"Bisleri ad @ 11:45 am for 30 mins",Top,Rb,Available
AD113,,Mumbai,,,"Company: 'Kurkure', scheduled at 10pm sharp, 1 hour",Side Bar,NRb,Available
AD114,Red Bull,Chennai,,,"Midnight Red Bull ad - duration 45 mins",Full Screen,Rb,Available
"""
with open("Ad_Calendar.csv", "w", encoding="utf-8") as f:
    f.write(csv_data)






