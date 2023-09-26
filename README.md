# CTTC  - Cyber Threat to Context

## Problem 

* ChatGPT can't interact with internet without a paid Plugin 
* Plugins are paid, and they have limited quote
* Plugins are not flexible
* Reading cyber threat updates can be time consuming


## Solution

I created a simple Flask Web application in Python to scrap data from given URL (blogpost or news about cyber threats) and send it to ChatGPT for giving us context about it such as:
  * Prevention against this threat
  * Detection against this threat
  * Summary about this threat

Below figures showing example usage of CTTC against threat report from SentinelOne: 


![CTTC_2](https://github.com/whichbuffer/CTTC/assets/42712921/b2b9f64f-efa8-4f0b-9715-c7b8534a8255)

![CTTC_1](https://github.com/whichbuffer/CTTC/assets/42712921/5010dfe1-4103-4f5b-b878-c28b37c9b321)





## Limitation 

Cyber Threat Intelligence (CTI) requires experienced human analysts, so this project is not equivalent of it. CTTC project only helps analysts to perform their CTI research in faster way by using ChatGPT Large language model.
ChatGPT may produce inaccurate information about people, places, or facts therefore CTTC needs to be used by only experienced human analysts.


