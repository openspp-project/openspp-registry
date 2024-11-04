# OpenSPP Event Demo

This module, **[spp_event_demo](spp_event_demo)**, provides demonstration data and functionalities for the **[spp_event_data](spp_event_demo](spp_event_data](spp_event_demo)**, provides demonstration data and functionalities for the **[spp_event_data)** module within the OpenSPP ecosystem. It showcases how to extend and utilize the event tracking capabilities of OpenSPP for specific use cases. 

## Relationship to spp_event_data

This module directly depends on and builds upon the functionalities of the **[spp_event_data](spp_event_data)** module. While **[spp_event_data](spp_event_data)** provides the core structure for recording and managing events related to registrants, **[spp_event_demo](spp_event_data](spp_event_demo](spp_event_data)** module. While **[spp_event_data](spp_event_data)** provides the core structure for recording and managing events related to registrants, **[spp_event_demo)** demonstrates practical applications of this system through concrete examples.

## Additional Functionality and Demonstrations

1. **Predefined Event Types**:
    * Introduces several predefined event types, including:
        * **House Visit (spp.event.house.visit)**: Captures data collected during a household visit, including farm details, livestock numbers, and food security indicators.
        * **Phone Survey (spp.event.phone.survey)**:  Records information gathered through a phone-based survey, such as a summary and detailed description of the conversation.
        * **School Enrollment Record (spp.event.schoolenrollment.record)**:  Tracks school enrollment events, storing details about the school, enrollment type, and date.

2. **Data Models and Views**:
    * Defines specific data models for each event type, each with relevant fields for capturing data.
    * Provides user-friendly views (tree and form) for each event type, allowing for easy data entry, viewing, and management within the Odoo interface.

3. **Event Creation Wizards**:
    * Includes dedicated wizards for creating new events:
        * **Create Event: House Visit**:  Guides users through the process of logging a house visit event, including capturing specific data points.
        * **Create Event: Phone Survey**: Simplifies the recording of phone survey events.
        * **Create Event: School Enrollment**: Facilitates the logging of school enrollment records.

4. **Integration with Registrant Profiles**:
    * Extends the registrant profiles to display active events of each type, providing a quick overview of the latest events associated with a particular registrant.

## Example Scenario

This module demonstrates how a program might use the **[spp_event_data](spp_event_data)** module.  For example, a user could record a series of house visits with a beneficiary.  Each house visit would be linked to the beneficiary's profile and the program could then query for all beneficiaries who have had at least one house visit, or all beneficiaries who have not had a house visit in the last 6 months. 

## Conclusion

The **[spp_event_demo](spp_event_demo)** module serves as a practical guide and starting point for implementing custom event tracking within OpenSPP.  By providing concrete examples and pre-built components, it empowers users to leverage the full potential of the **[spp_event_data](spp_event_demo](spp_event_data](spp_event_demo)** module serves as a practical guide and starting point for implementing custom event tracking within OpenSPP.  By providing concrete examples and pre-built components, it empowers users to leverage the full potential of the **[spp_event_data)** module and tailor it to their specific program needs. 
