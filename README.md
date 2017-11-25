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

## KAYAK API

-  Field Departure : `/mv/marvel?f=h&where=cac&s=58&lc_cc=KR&lc=ko&v=v2&cv=4`
- Field Destination: `/mv/marvel?f=h&where=gmp&s=58&lc_cc=KR&lc=ko&v=v2&cv=4`

They both look the same, so we can see that the payload is after the "where" in the URI.

The paylaod we are going to use to carry out our attack is in the form:
`/mv/marvel?f=h&where=[GENERATED]&s=58&lc_cc=KR&lc=ko&v=v2&cv=4`, where [GENERATED] is a string potentially entered by the user. Note that we observed that no destination name was more that 15 characters. So we can limit the length of the generated string to 15. (Note: For efficiency measures, we can try to find until how many characters we can uniquely identify every destination/depearture, in order to generate a minimum number of payloads, and fasten the search by limiting the number of time we will do calls on the API which will result in a smaller tree)


