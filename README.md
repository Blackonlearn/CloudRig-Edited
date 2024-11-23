<!-- FEATURES -->
## Contact:
- [ ] https://instagram.com/bong.qhi/
- [ ] https://threads.net/@bong.qhi
- [ ] https://twitter.com/midclips


# Custom Cloud Rig
CloudRig is a powerful rigging add-on for Blender, built to extend and enhance the capabilities of the default Rigify add-on. With advanced automation and customizable features, CloudRig allows animators and riggers to create complex, production-ready rigs with ease.
This project enhances Blender's CloudRig add-on by introducing the ability to set a custom basename for your rig. The basename dynamically updates key elements of the rig and generates a UI panel category that corresponds to the basename.


## What is it ?

https://github.com/user-attachments/assets/ad755d32-01d5-4a48-ba26-870f6a1c4cd2



#### -> Notice that meta rig and actual rig from Monkey into something entered to the rig name text column

![SS-CLOUDRIG (2)](https://github.com/user-attachments/assets/3b6f6ad0-cd86-41b9-9771-9e1b28d451bd)
![SS-CLOUDRIG](https://github.com/user-attachments/assets/ad8e3969-e828-43fb-965c-cd3aefd5211a)






## Features


1. **Custom Basename Support (RIGIFY Integrated):**
      - [ ] Define a custom basename using the rigify_rig_basename property in the Armature's data.
      - [ ] Automatically rename:
          - The RIG object and its associated RIG data.
          - The META object and its associated META data.
          - The Text Block used for UI Panel
2. **Dynamic UI Panel Category:**
      - [ ] The CLOUD RIG UI panel appears in the N-panel under a category matching the rig's basename
      - [ ] Combine Cloud Rig Panel with RIGIFY panel if both are used
      - [ ] If no basename is set, it defaults to "CloudRig".

## Installation

### **Step 1: Clone or Download:**
   ```sh
   git clone https://github.com/Blackonlearn/RIGIFY-Edited
   ```
### **Step 2: Locate Blender's Add-ons Directory:**
   - Windows
   ```sh
   C:\Users\{ChangeThisWithYourPCUserNameAndDeleteTheBracket}\AppData\Roaming\Blender Foundation\Blender\3.6\scripts\rigify\CloudRig_master
   ```
   - Linux
   ```sh
   /home/{ChangeThisWithYourPCUserNameAndDeleteTheBracket}/.config/blender/3.6/scripts/rigify/CloudRig_master
   ```
   - macOS
   ```sh
   /Users/{ChangeThisWithYourPCUserNameAndDeleteTheBracket}/Library/Application Support/Blender/3.6/scripts/rigify/CloudRig_master
   ```
### **Step 3: Replace the Files:**
   Copy and replace the modified files into the CloudRig folder:
   - ui/replace_rigify_ui.py
   - generation/cloud_generator.py
   - generation/cloudrig.py
   
### **Step 4: Restart Blender**
   Restart Blender to ensure the updated CloudRig add-on is loaded.

### **Step 5: Enable Rigify**
    1. Open Edit > Preferences > Add Ons > Rigify.
    2. Search for CloudRig and ensure it is enabled
