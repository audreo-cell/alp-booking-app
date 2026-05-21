# ALP Booking App TODO

## Database & Backend
- [x] Create slots table schema in drizzle/schema.ts
- [x] Create bookings table schema in drizzle/schema.ts
- [x] Generate and apply database migration
- [x] Add query helpers in server/db.ts for slots and bookings
- [x] Create tRPC procedures for public booking operations
- [x] Create tRPC procedures for admin operations (login, view, cancel, delete, add slots, export)

## Public Booking Page
- [x] Display heading "ALP Group Consultation Slots"
- [x] Display introductory text
- [x] Display time slots grouped by date (Friday 3 July 2026, Monday 13 July 2026)
- [x] Sort slots chronologically from 9:00am to 5:00pm
- [x] Style available slots as selectable buttons
- [x] Style booked slots as greyed out and unselectable
- [x] Implement slot selection flow (click slot → enter name → confirmation)
- [x] Display confirmation screen with name, date, time, and venue (Room C2B)
- [x] Add subtle "Admin Panel" link in footer

## Admin Panel
- [x] Create login page at /admin
- [x] Implement username/password authentication
- [x] Ensure login page always appears first regardless of session state
- [x] Display all booked slots with booker names
- [x] Display all available slots
- [x] Add Cancel button for each booked slot
- [x] Add Delete button for each available slot
- [x] Implement export to .xlsx with columns: Name, Date, Time Slot
- [x] Add form to create new time slots (date and time input)
- [x] Implement logout button that returns to public page

## Styling & UX
- [x] Apply clean, minimal design with white/grey color scheme
- [x] Ensure mobile-friendly responsive layout
- [x] Use clear typography
- [x] No animations or branding elements
- [x] Ensure all text is readable against backgrounds

## Testing & Deployment
- [x] Test public booking flow end-to-end
- [x] Test admin login and session management
- [x] Test slot management (add, cancel, delete)
- [x] Test export functionality
- [x] Verify all constraints are met
- [x] Create checkpoint and deploy
