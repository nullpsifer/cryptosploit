# Cryptosploit

Cryptosploit is a Metasploit-like tool designed to streamline the exploitation of vulnerable cryptosystems in real-world situations. A core principle of the Cryptosploit project is that code that preforms cryptographic attacks should not be tightly coupled to code that interact with cryptosystems. Cryptosploit stores code that conducts cryptographic attacks (and auxiliary tasks) in self-contain "module" files that are easy to write, maintain, and share. It stores code that modules use to interact with specific implementations of cryptosystems in "oracle files." Do you want to run the same attack on a cryptosystem that accepts input via HTTP POST requests and a cryptosystem that accepts input via COM ports? No problem! Just change your module's oracle selection.

## Basic Use

Launching Cryptosploit drops the user into an interactive console environment:

![cryptosploit](https://user-images.githubusercontent.com/29503289/181995085-8e344e2f-eea8-4861-975d-3162ac67e1d2.PNG)

The "help" command lists a description of all available comands:

![help](https://user-images.githubusercontent.com/29503289/181995292-19433a13-92f2-4d06-907e-b959769fa420.png)

To set module and oracle arguments, use the `set` command. Note that to distinguish module arguments from oracle arguments, oracle arguments must be specified with an "o:" prefix. To set a module argument called "modarg" to "X", you would use `set modarg X`. To set an oracle argument called "oraclearg" to "Y", you would use `set o:oraclearg Y`.

## Example: Padding Oracle Attack

In this example, a web application accepts ciphertexts as a URL parameter named "ctext" and sends a different response code for good and bad plaintext paddings. URLs are of the form `http://localhost:5054/padding-oracle/oracle?ctext=C9FF... ciphertext here ...D529`. The web_status_boolean_oracle is used.

![padding_oracle](https://user-images.githubusercontent.com/29503289/181995548-ea96bb29-ae0c-4a7c-b9cf-a845155ee167.png)

A full video of the attack in action can be found [here](https://www.youtube.com/watch?v=AQv32XPD0jk).

## Writing a Module

Modules are stored in the "modules" folder. When Cryptosploit starts it automatically loads information about all modules in this folder into memory. Installing a new module is as simple as dropping it into this folder. All modules must extend the "AbstractModule" class. Modules are required to have a name and description for the `listmods` module table, a list of arguments, and a flag to specify if an oracle is required (oracles are unnecessary for some auxiliary modules), and optionally a default oracle.

![sample module](https://user-images.githubusercontent.com/29503289/181996201-d2cd29c9-2f60-47b4-bbe6-f1d1a0ce7358.png)

## Writing an Oracle

Oracles are stored in the "oracles" folder. Like modules, information about oracles is automatically loaded when Cryptosploit starts. All oracles must extend the "AbstractOracle" class. Oracles are required to have names, descriptions, argument lists, and a "makeoracle" function. The "makeoracle" function returns an oracle function, which is responsible for communicating with a specific cryptosystem on behalf of modules and relaying necessary information back to them. Oracles abstract attack code from the implementation details of the cryptosystems that they are attacking.

![sample oracle](https://user-images.githubusercontent.com/29503289/181996397-337f17e8-5399-42f8-b22a-a7efb7e8f0a2.png)

## Installing

Cryptosploit can be installed with `pipenv install`. For Windows, install git and the pyreadline3 package prior to running this command.
