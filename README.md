# Conference Crawler
Support Conference List
- [x] VLDB Conference  
    - [VLDB 2021](https://vldb.org/2021/?papers-research) 

- [ ] FAST Conference 
- [ ] OSDI Conference
- [ ] SOSP Conference
- [ ] ATC Conference
- [ ] SIGMOD COnference

# Environment Setup
execute the setup script
```
chmod +x env_setup.sh && ./env_setup.sh
```

# Run the craw script
For VLDB
```
cd vldb_crawler
python3 get_paper_list.py
```