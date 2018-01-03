// Copyright (C) 2014 Ondřej Garncarz
// License: AGPLv3+

#include <Python.h>

int enctype2_encoder(unsigned char *key, unsigned char *data, int size);
unsigned char *enctype2_decoder(unsigned char *key, unsigned char *data, int *size);

static PyObject* encode_list(PyObject* self, PyObject* args) {
	unsigned char *key, *data_arg, *data;
	int size, ret_size;
	PyObject *ret;
	
	if (!PyArg_ParseTuple(args, "sy#", &key, &data_arg, &size)) {
		return NULL;
	}

	data = (unsigned char*)malloc(2 * size * sizeof(unsigned char) + 1 + 8 + 6);
	memcpy(data, data_arg, size * sizeof(unsigned char));

	ret_size = enctype2_encoder(key, data, size);

	ret = Py_BuildValue("y#", data, ret_size - 1);
	free(data);
	
	return ret;
}

static PyObject* decode_list(PyObject* self, PyObject* args) {
	unsigned char *key, *data_arg, *data, *data_ret;
	int size_arg, size;
	PyObject *ret;

	if (!PyArg_ParseTuple(args, "sy#", &key, &data_arg, &size_arg)) {
		return NULL;
	}

	size = size_arg;

	data = (unsigned char*)malloc(2 * size * sizeof(unsigned char));
	memcpy(data, data_arg, size * sizeof(unsigned char));

	data_ret = enctype2_decoder(key, data, &size);

	ret = Py_BuildValue("y#", data_ret, size);
	free(data);
	// free(data_ret); leads to "invalid pointer"

	return ret;
}

static PyMethodDef aluigiMethods[] = {
	{"encode_list", encode_list, METH_VARARGS},
	{"decode_list", decode_list, METH_VARARGS},
	{NULL, NULL}
};

static struct PyModuleDef aluigiModule = {
	PyModuleDef_HEAD_INIT,
	"aluigi",
	NULL,
	0,
	aluigiMethods
};

PyMODINIT_FUNC PyInit_aluigi(void) {
	return PyModule_Create(&aluigiModule);
}

