# OpenSPP Starter Module

This module serves as the starting point for configuring and launching a new OpenSPP instance. It doesn't introduce any specific business logic or data models related to social protection programs or farmer registries. Instead, it focuses on providing a basic setup and customization options for the OpenSPP platform.

## Functionality

* **Configuration:** The module allows administrators to enable or disable the display of a custom menu entry that directs users to the OpenSPP modules and functionalities.
* **User Interface:** It can replace the standard Odoo "Management" menu with a dedicated OpenSPP menu, guiding users towards the relevant features for managing social protection programs and farmer registries.

## Dependencies

* **base:** This module depends on the Odoo base module, inheriting its functionality for menus and user interface elements.

## Integration

The [spp_starter](spp_starter) module doesn't directly integrate with other specific modules related to social protection or farmer registries. However, it acts as a foundation upon which other modules can build and extend the platform's capabilities. By modifying the menu structure and providing configuration options, it prepares the system for the installation and utilization of more specialized modules. 

## Key Components

* **ir.config_parameter:** Utilizes configuration parameters to control the visibility of the OpenSPP menu entry, allowing administrators to customize the user experience based on the specific implementation needs.
* **ir.ui.menu:** Inherits from the `ir.ui.menu` model to override the default menu visibility, replacing the standard "Management" menu with an OpenSPP-specific menu when configured.

## Usage

Once the module is installed, administrators can configure the visibility of the OpenSPP menu entry by accessing the system parameters. Depending on the chosen configuration, users will see either the standard Odoo "Management" menu or a custom OpenSPP menu, guiding them to the relevant sections for managing social protection programs and farmer registries. 
