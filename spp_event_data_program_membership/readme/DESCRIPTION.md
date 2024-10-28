# OpenSPP Event Data Program Membership

This module enhances the functionality of OpenSPP by integrating the **Event Data** module ([spp_event_data](spp_event_data)) with the **G2P Programs** module ([g2p_programs](spp_event_data](g2p_programs](spp_event_data)) with the **G2P Programs** module ([g2p_programs)). It allows users to record and track program membership-related events within the OpenSPP system.

## Purpose

The **spp_event_data_program_membership** module serves to:

* **Record Program Membership Events:**  Log specific events related to program membership, such as enrollment, suspension, exit, and changes in eligibility status.
* **Link Events to Program Memberships:** Associate these events with the corresponding program membership records in the [g2p_programs](g2p_programs) module.
* **Provide an Event History:** Offer a comprehensive history of events associated with each program membership, facilitating tracking and auditing.

## Module Integration

1. **[spp_event_data](spp_event_data):** This module leverages the event data framework provided by the [spp_event_data](spp_event_data](spp_event_data](spp_event_data):** This module leverages the event data framework provided by the [spp_event_data) module to record and manage event information.
2. **[g2p_programs](g2p_programs):**  It integrates directly with the [g2p_programs](g2p_programs](g2p_programs](g2p_programs):**  It integrates directly with the [g2p_programs) module, linking event data to the relevant program membership records (`g2p.program_membership` model). 

## Additional Functionality

* **Program Membership Field in Event Data:**
    * Adds a `program_membership_id` field to the `spp.event.data` model, allowing users to directly associate an event with a specific program membership.
    * Includes a computed domain (`program_membership_id_domain`) to dynamically filter and display only relevant program memberships based on the selected partner.

* **Modified Event Data Views:**
    * Updates the event data form view (`view_spp_event_data_form_custom`) to include the new `program_membership_id` field. 
    * Enables users to select the relevant program membership when creating or editing an event.

* **Read-Only Event Data Fields on Registrant Form:**
    * Modifies the registrant form view (`view_groups_event_data_form_custom`) to display event data in read-only mode.
    * Prevents accidental modification of event data from the registrant's profile. 

## Usage Example

1. **Recording an Enrollment Event:** A program officer enrolls a beneficiary into a social assistance program. Using this module, they can create a new event of type "Enrollment," link it to the beneficiary's newly created program membership record, and record relevant details, such as the enrollment date. 

2. **Tracking Eligibility Changes:**  A beneficiary's eligibility status changes due to a change in their circumstances. A program officer can record this event, selecting "Eligibility Change" as the event type and associating it with the beneficiary's program membership.  

3. **Viewing Event History:**  Program staff can access a beneficiary's program membership record and view a chronological list of all events, providing a clear audit trail of their participation in the program.

## Conclusion

The **spp_event_data_program_membership** module enhances the tracking and management of program membership events within OpenSPP.  By integrating event data with program memberships, it improves data integrity, transparency, and the overall efficiency of program administration. 
