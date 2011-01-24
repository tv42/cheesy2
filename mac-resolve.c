#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <linux/if_arp.h>
#include <sys/ioctl.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

/*
  NOTE: This lookup will only complete if the entry happens to be in
  the cache; it does not actually go out and send a request to the
  network. In the cheesy2 use case, that's perfectly fine.
 */

int main(int argc, char ** argv) {
  int s;
  char *iface;
  char *ipaddr;
  struct arpreq a;
  struct sockaddr_in * sin;

  if (argc != 3) {
    errx(2, "usage: %s INTERFACE IPADDR", argv[0]);
  }
  iface = argv[1];
  ipaddr = argv[2];

  s = socket(AF_INET,SOCK_DGRAM,0);
  if (s < 0) {
    perror("socket");
    exit(1);
  }
  memset(&a, 0, sizeof(a));
  strcpy(a.arp_dev, iface);
  sin = (struct sockaddr_in *) &(a.arp_pa);
  sin->sin_family = AF_INET;

  if (!inet_aton(ipaddr, &sin->sin_addr)) {
    errx(1, "Cannot convert ip address: %s", ipaddr);
  }
  if (ioctl(s, SIOCGARP, &a)) {
    err(1, "getting ARP info");
  }
  if (!(a.arp_flags & ATF_COM)) {
    errx(1, "Lookup did not complete");
  }
  printf("%02x-%02x-%02x-%02x-%02x-%02x\n",
	 a.arp_ha.sa_data[0] & 0xFF,
	 a.arp_ha.sa_data[1] & 0xFF,
	 a.arp_ha.sa_data[2] & 0xFF,
	 a.arp_ha.sa_data[3] & 0xFF,
	 a.arp_ha.sa_data[4] & 0xFF,
	 a.arp_ha.sa_data[5] & 0xFF);
  return 0;
}
