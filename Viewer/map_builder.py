# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 10:21:40 2013

@author: Leon
"""
import numpy

from traits.api\
    import HasTraits, Int, Array, Enum, Bool

class MapBuilder(HasTraits):
    """
    """

    mode = Enum('basic', 'reverse', 'sort')
    transpose = Bool
    length = Int
    first_index = Int
    available_length = Int
    parity = Enum((1, -1))

    _data_x = Array
    _data_y = Array
    _algo_known = Bool(False)

    def set_data_x(self, data_x):
        """
        """
        self._data_x = data_x
        self._compute_algo()

    def set_data_y(self, data_y):
        """
        """
        self._data_y = data_y
        self._compute_algo()

    def update_data_x(self, update_x):
        """
        """
        self._data_x = numpy.concatenate((self._data_x, update_x))
        if not self._algo_known:
            self._compute_algo()
        elif self.transpose:
            self.length = len(set(self._data_x))

    def update_data_y(self, update_y):
        """
        """
        self._data_y = numpy.concatenate((self._data_y, update_y))
        if not self._algo_known:
            self._compute_algo()
        elif not self.transpose:
            self.length = len(set(self._data_y))

    def build_map(self, data_c):
        """
        """
        made_copy = False
        raw_len = len(data_c)
        current_pos = raw_len % self.length
        print 'map builder buildmap raw_len, length = {}, {}'.format(raw_len, self.length)
        data_x = self._data_x
        data_y = self._data_y
        if current_pos != 0:
            last = data_c[-1]
            data_c = numpy.append(data_c,
                            last*numpy.ones(self.length - current_pos))
            data_x = numpy.append(data_x,
                            max(data_x)*numpy.ones(self.length - current_pos))
            data_y = numpy.append(data_y,
                            max(data_y)*numpy.ones(self.length - current_pos))
            self.made_copy = True

        self.available_length = len(data_c) - raw_len
        print 'map builder buildmap len = {}'.format(len(data_c))

        if self.mode == 'basic':
            self.first_index = raw_len

        elif self.mode == 'reverse':
            index = numpy.arange(len(data_c))
            l = self.length
            index = index*(1+self.parity*(-1)**(index/l))/2 +\
                ((index/l+1)*l-index%l-1)*(1+self.parity*(-1)**(index/l+1))/2

            self.parity = (-1)**(raw_len/l)
            data_c = data_c[index]
            made_copy = True
            if self.parity == 1:
                self.first_index = raw_len
            else:
                self.first_index = self.length*raw_len/self.length

        else:
            if self.transpose:
                index = numpy.lexsort((data_x, data_y))
            else:
                index = numpy.lexsort((data_y, data_x))
            data_c = data_c[index]
            made_copy = True

        if not self.transpose:
            return numpy.reshape(data_c, (self.length, -1), order = 'F'),\
                    made_copy
        else:
            return numpy.reshape(data_c,(self.length, -1), order = 'F').T,\
                    made_copy

    def update_map(self, update, data_plot, data):
        """
        """
        raw_data = False
        if self.transpose:
            aux = numpy.ravel(data_plot.T, order = 'F')
        else:
            aux = numpy.ravel(data_plot, order = 'F')
        len_update = len(update)
        size = min((self.available_length, len_update))
        print 'map_builder update size, len_update = {},{}'.format(size,len_update)
        if self.mode == 'basic':
            if size != 0:
                aux[self.first_index:self.first_index+size] = update[0:size]
            if size != len_update:
                len_to_add = self.length*\
                                ((len_update-size+self.length-1)/self.length)
                print 'map_builder update length, len_to_add = {}, {}'.format(self.length, len_to_add)
                aux = numpy.append(aux, numpy.zeros(len_to_add))
                aux[self.first_index+size:self.first_index+len_update] =\
                    update[size:len_update]

            self.first_index += len_update
            self.available_length = len(aux)- self.first_index
            if self.available_length != 0:
                aux[self.first_index:len(aux)] = update[-1]

        elif self.mode == 'reverse':
            if self.parity == 1:
                aux[self.first_index:self.first_index+size] = update[0:size]
            else:
                aux[self.first_inde:self.first_index+size] = \
                                                        update.reverse[0:size]
            if size != len_update:
                len_to_add = self.length*\
                                ((len_update-size+self.length-1)/self.length)
                aux = numpy.append(aux, numpy.zeros(len_to_add))
                self.parity *= -1
                update = update[size::]
                index = numpy.arange(len(update))
                l = self.length
                index = (1+self.parity*(-1)**(index/l))/2*index + \
                            ((index/l+1)*l-index%l-1)*\
                            (1+self.parity*(-1)**(index/l+1))/2

                update = update[index]
                self.first_index += self.length
                aux[self.first_index:self.first_index+len(update)]= update[::]
                self.first_index += len(update)
                self.parity = (-1)**(self.first_index/self.length)

            if self.avalable_length != 0:
                aux[self.first_index+len_update:len(aux)] = update[-1]

        else:
            data_c = data
            data_x = self._data_x
            data_y = self._data_y
            if len(data_c) % self.length != 0:
                last = data_c[-1]
                len_to_add = self.length - len(data_c) % self.length
                data_c = numpy.append(data_c,
                                last*numpy.ones(len_to_add))
                data_x = numpy.append(data_x,
                                max(data_x)*numpy.ones(len_to_add))
                data_y = numpy.append(data_y,
                                max(data_y)*numpy.ones(len_to_add))
                print 'map_builder update sort len_to_add = {}'.format(len_to_add)

            index = numpy.lexsort((data_y,data_x))
            aux = data_c[index]
            raw_data = True
            print 'map_builder update sort len, error = {},{}'.format(len(data_c),len(aux))

        if not self.transpose:
            return numpy.reshape(aux, (self.length,-1), order = 'F'),\
                                                                    raw_data
        else:
            return numpy.reshape(aux, (self.length, -1), order = 'F').T,\
                                                                    raw_data

    def _compute_algo(self):
        """
        """
        if self._data_x != [] and self._data_y != []:
            dimx = len(set(self._data_x))
            dimy = len(set(self._data_y))
            self.length = 1

            if self._data_x[0] == self._data_x[1]:
                if dimy != 0:
                    self.length = dimy
                self.transpose = False
                if len(self._data_y) > dimy:
                    self._algo_known = True
                    if self._data_y[0] == self._data_y[dimy]:
                        self.mode = 'basic'
                    elif self._data_y[dimy-1] == self._data_y[dimy]:
                        self.mode = 'reverse'
                        if self._data_y[0] < self._data_y[1]:
                            self.parity = 1
                        else:
                            self.parity = -1
                    else:
                        self.mode = 'sort'
                else:
                    self.mode = 'sort'
                    self._algo_known = False

            elif self._data_y[0] == self._data_y[1]:
                if dimx !=0:
                    self.length = dimx
                self.transpose = True
                if len(self._data_x) > dimx:
                    self._algo_known = True
                    if self._data_x[0] == self._data_x[dimx]:
                        self.mode = 'basic'
                    elif self._data_x[dimx-1] == self._data_x[dimx]:
                        self.mode = 'reverse'
                        if self._data_x[0] < self._data_x[1]:
                            self.parity = 1
                        else:
                            self.parity = -1
                    else:
                        self.mode = 'sort'
                else:
                    self.mode = 'sort'
                    self._algo_known = False

            if dimy == 1 or dimx == 1:
                self._algo_known = False

        print 'map_builder compute_algo mode = {}'.format(self.mode)

if __name__ == '__main__':
    from pylab import pcolor, colorbar, show, figure
    #Basic F
    x = numpy.arange(10).repeat(9)
    y = numpy.tile(numpy.arange(9), 10)
    c = numpy.arange(88)
    mapB = MapBuilder()
    mapB._data_x = x
    mapB._data_y = y
    pcolor(mapB.build_map(c))
    colorbar()
    show()
    mapB._data_x = y
    mapB._data_y = x
    figure(2)
    pcolor(mapB.build_map(c).T)
    colorbar()
    show()

    #Reversed F
    x = numpy.arange(9).repeat(9)
    y = numpy.append(numpy.tile(numpy.append(numpy.arange(9),
                                    numpy.arange(8,-1,-1)),8),numpy.arange(9))
    mapB._data_x = x
    mapB._data_y = y
    figure(3)
    pcolor(mapB.build_map(c))
    colorbar()
    show()