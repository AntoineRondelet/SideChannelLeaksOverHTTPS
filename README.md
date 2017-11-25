# Project of CS548: Network analysis and Side Channel Leaks

### Software implementation
- Use PyShark to do some network analysis
- Input of the entire tool:
  - URL of the website 
  - The input should also contain the IP addresses of:
    - The victim/target
    - The web app the victim is using
  - URL that are used by the web app to fetch data as the user does some input (the URL used to fetch data with AJAX calls) + maybe a cookie or at least of information needed to be able to do the call(different from one API to another)
    - And also all the information needed to generate all the possible calls: (type of payload we need to generate, limit length and so on...)
    - That way we would be able to generate all kind of paylaod and add them to the URL to do some API calls and get the sizes associated with the user input
  - Build a tree containing all the possible input and the corresponding packet size
  - Using the tree built in the previous step, detect the user input that is the most likely to have had happen

### Ideas

- It can be interesting to speak about the SC leaks discovered in the eventLoop of chrome
  - Coupled with network analysis, this could be very efficient and could guarantee a malicious user/attacker to be almost sure on what the victim is actually doing on his computer
