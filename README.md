# Dynamic Resolution Exploration README

## General Information
* Author: Thomas Williams
* Date: 1/16/2-25
* Description: This is code and slides that explore the Dynamic Resolution techniques described in the MITRE ATT&CK Framework and are used frequently in C2 style cyber attacks.

## Why You Should Care
DGAs and more generally, Dynamic Resolution make detection difficult for C2 URLs. Understanding DGAs, Fast Flux DNS, and DNS Calculation in more detail will help researchers to develop better detection methods, perhaps with the help of artificial intelligence and/or machine learning.

Behind many modern C2 attacks, and to some degree, other forms of malware and general cyber attacks, sits the entirety of Dynamic Resolution techniques. While not directly causing malware, these techniques allow for malware to go undetected for longer, providing plenty of time for attackers to gather more information, steal more data and finances from unsuspecting victims, and generally wreak havoc for IT teams. Knowing what is possible and how it works can only improve existing detection methods.

## Three Main Ideas
1. Domain Generating Algorithms (DGAs) actually have valid uses, but are infrequently used in this manner due to the complexity. They serve as one of three Dynamic Resolution techniques for randomzing the URL for a C2 attack as well as other attacks.
2. Fast Flux DNS (single and dual) serves as a way to randomize the IP address associated with a DNS address, making harder for defenders. These also have a valid use in load balancing, but again, are more frequently used in attacks.
3. DNS Calculation is a newer technique in the Dynamic Resolution family, dedicated primarily to dynamic generation of ports and secondarily of IP addresses. This method has few, if any, valid uses other than attacks.

## Future Direction
An interesting next step for this topic would be to see if Dynamic Resolution is more detectable with techniques that reach out to the public internet for seed values as they are potentially more noticeable to firewalls, but potentially blend into the rest of traffic enough that they would not be found. Additionally, dynamic port generation only has one example in the ATT&CK Framework, so exploration of that portion of Dynamic Resolution could be fruitful.


## Additional Resources
* [What is DNS Fast Flux? - Cloudflare](https://www.cloudflare.com/learning/dns/dns-fast-flux/)
* [MITRE ATT&CK Framework - Dynamic Resolution](https://attack.mitre.org/techniques/T1568/)
* [Fast Flux 101](https://unit42.paloaltonetworks.com/fast-flux-101/) - This also covers Dynamic Resolution in general, with pictures.



