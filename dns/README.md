# DNS

The Ultimate Hosts Blacklist project offers 2 DNS servers that are updated
daily. They are free to use and can be used instead of the other list we offer.

Both DNS servers are located in Germany. They are configured to answer DNS
queries with the [bind](https://www.isc.org/bind/) DNS implementation software.

Our project follows a Zero-Logging policy. Meaning that we don't store any
information about your queries nor their answers.

### Location

Our servers are reachable

| DNS Name | safedns.allover.co.za   | safedns2.allover.co.za  |
| -------- | ----------------------- | ----------------------- |
| IPv4     | `88.198.70.38`          | `88.198.70.39`          |
| IPv6     | `2a01:4f8:140:5021::38` | `2a01:4f8:140:5021::39` |

### Testing

After each successful launch of our self-crafted software, the
`xxx.allover.co.za` domain is added into one of the generated RPZ zones.

Therefore, one can test through the following - or their equivalent for your
system or distribution.

IPv4:

```shell
$ dig +short -t A xxx.allover.co.za @safedns.allover.co.za
0.0.0.0
$ dig +short -t A xxx.allover.co.za @safedns2.allover.co.za
0.0.0.0
```

IPv6:

```shell
$ dig +short -t AAAA xxx.allover.co.za @safedns.allover.co.za
::
$ dig +short -t AAAA xxx.allover.co.za @safedns2.allover.co.za
::
```

### Configuration

Our servers are configured as masters. There is no Master/Slave constellation.

A self-crafted software that merges all data from and create the RPZ zones out
of them is automatically running every night or on-demand.

Our logging configuration is the following:

```
logging {
    category default { null; };
};
```
