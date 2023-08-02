# Introduction 
TODO: Give a short introduction of your project. Let this section explain the objectives or the motivation behind this project. 

# Getting Started
TODO: Guide users through getting your code up and running on their own system. In this section you can talk about:
1.	Installation process
2.	Software dependencies
3.	Latest releases
4.	API references

# Build and Test
TODO: Describe and show how to build your code and run the tests. 

# Contribute
TODO: Explain how other users and developers can contribute to make your code better. 

If you want to learn more about creating good readme files then refer the following [guidelines](https://docs.microsoft.com/en-us/azure/devops/repos/git/create-a-readme?view=azure-devops). You can also seek inspiration from the below readme files:
- [ASP.NET Core](https://github.com/aspnet/Home)
- [Visual Studio Code](https://github.com/Microsoft/vscode)
- [Chakra Core](https://github.com/Microsoft/ChakraCore)

#### NOTES:
PayScaleLinks.json acts as a catalogue of sorts. For each main key the following information is provided:
- desc: Description of of hyperlink reference (href) from main page
    # Note: instances where there are more than one href pointing to the same page, the first instance will be used as
    #   the main key (ex: main key AU)
- href: page containing all tables related to the main key
- codes: all main keys related to the main key reference (see note above)
- captions: all captions contained in tables related to main keys
    # Note: caption key 'other' is used as a catch all key for all other related captioned tables that do not reference
    #   a main key
- missing: any main keys that did not yield any related tables.
    # Note: only captured if multiple main keys or no tables captured.
    * Presently missing: EST, LAT, EU, SR(W), GS - due to differential formatting (not referencing related code or annual pay in table caption)

PayScaleTables.json contains jsonified dataframes and footer or tables separated:
- unicode characters have been changed to plain text (ascii)
- table references to footer have been separated by space from rest of cell (in some range columns and all date columns)
- \n formatting in footer kept for time being for ease of reading - can be manipulated if needed depending on output.
- most step columns contain numeric values (int/float)
- range columns contain text (str), as do some non range columns
    # Note: only code with some non-range step columns with table references are DS, which seems to reference irrelevant information (collective agreement, which is    previously referenced)