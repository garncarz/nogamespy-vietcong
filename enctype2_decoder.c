/*

GS enctype2 servers list decoder/encoder 0.1.2
by Luigi Auriemma
e-mail: aluigi@autistici.org
web:    aluigi.org


INTRODUCTION
============
This is the algorithm used to decrypt the data sent by the Gamespy
master server (or any other compatible server) using the enctype 2
method.


USAGE
=====
Add the following prototype at the beginning of your code:

  unsigned char *enctype2_decoder(unsigned char *, unsigned char *, int *);

then use:

        pointer = enctype2_decoder(
            gamekey,        // the gamekey
            buffer,         // all the data received from the master server
            &buffer_len);   // the size of the master server

The return value is a pointer to the decrypted zone of buffer and
buffer_len is modified with the size of the decrypted data.

A simpler way to use the function is just using:

  len = enctype2_wrapper(key, data, data_len);


THANX TO
========
REC (http://www.backerstreet.com/rec/rec.htm) which has helped me in many
parts of the code.


LICENSE
=======
    Copyright 2004-2014 Luigi Auriemma

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA

    http://www.gnu.org/licenses/gpl.txt

*/

#include <string.h>



void encshare1(unsigned int *tbuff, unsigned char *datap, int len);
void encshare4(unsigned char *src, int size, unsigned int *dest);



unsigned char *enctype2_decoder(unsigned char *key, unsigned char *data, int *size) {
    unsigned int    dest[326];
    int             i;
    unsigned char   *datap;

    *data ^= 0xec;
    datap = data + 1;

    for(i = 0; key[i]; i++) datap[i] ^= key[i];

    for(i = 0; i < 326; i++) dest[i] = 0;
    if(*data) encshare4(datap, *data, dest);

    datap += *data;
    *size -= (*data + 1);
    if(*size < 6) {
        *size = 0;
        return(data);
    }

    encshare1(dest, datap, *size);

    *size -= 6;
    return(datap);
}



int enctype2_wrapper(unsigned char *key, unsigned char *data, int size) {
    unsigned char   *p;
    int     i;

    p = enctype2_decoder(key, data, &size);

    //memmove(data, p, size);   // memmove works but is untrusted
    if(p > data) {
        for(i = 0; i < size; i++) {
            data[i] = p[i];
        }
    }
    return(size);
}



/*
data must be big enough to contain also the following bytes: 1 + 8 + 6
*/
int enctype2_encoder(unsigned char *key, unsigned char *data, int size) {
    unsigned int    dest[326];
    int             i;
    unsigned char   *datap;
    int             header_size = 8;

    for(i = size - 1; i >= 0; i--) {
        data[1 + header_size + i] = data[i];
    }
    *data = header_size;
    
    datap = data + 1;
    memset(datap, 0, *data);

    for(i = 256; i < 326; i++) dest[i] = 0;
    encshare4(datap, *data, dest);

    memset(data + 1 + *data + size, 0, 6);
    encshare1(dest, datap + *data, size + 6);

    for(i = 0; key[i]; i++) datap[i] ^= key[i];
    size += 1 + *data + 6;
    *data ^= 0xec;
    return size;
}

