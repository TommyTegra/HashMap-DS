# Name: Tommy Nguyen
# OSU Email: nguyeto2@oregonstate.edu
# Course: CS261 - Data Structures
# Assignment: 6 - HashMap Implementation
# Due Date: 8/15/2023 @ 11:59 PM PDT
# Description: A series of methods to implement in order
#       to achieve a working implementation of a HashMap
#       which utilizes open addressing as a resolution
#       to collisions.


from a6_include import (DynamicArray, DynamicArrayException, HashEntry,
                        hash_function_1, hash_function_2)


class HashMap:
    def __init__(self, capacity: int, function) -> None:
        """
        Initialize new HashMap that uses
        quadratic probing for collision resolution
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        self._buckets = DynamicArray()

        # capacity must be a prime number
        self._capacity = self._next_prime(capacity)
        for _ in range(self._capacity):
            self._buckets.append(None)

        self._hash_function = function
        self._size = 0

    def __str__(self) -> str:
        """
        Override string method to provide more readable output
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        out = ''
        for i in range(self._buckets.length()):
            out += str(i) + ': ' + str(self._buckets[i]) + '\n'
        return out

    def _next_prime(self, capacity: int) -> int:
        """
        Increment from given number to find the closest prime number
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        if capacity % 2 == 0:
            capacity += 1

        while not self._is_prime(capacity):
            capacity += 2

        return capacity

    @staticmethod
    def _is_prime(capacity: int) -> bool:
        """
        Determine if given integer is a prime number and return boolean
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        if capacity == 2 or capacity == 3:
            return True

        if capacity == 1 or capacity % 2 == 0:
            return False

        factor = 3
        while factor ** 2 <= capacity:
            if capacity % factor == 0:
                return False
            factor += 2

        return True

    def get_size(self) -> int:
        """
        Return size of map
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        return self._size

    def get_capacity(self) -> int:
        """
        Return capacity of map
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        return self._capacity

    # ------------------------------------------------------------------ #

    def put(self, key: str, value: object) -> None:
        """
        Adds a key/value pair to the hash map. If the pairing
        already exists, quadratic probing is implemented as a
        collision resolution.
        """
        # Performs a resize, if needed
        if self.table_load() >= 0.5:
            self.resize_table(self._capacity * 2)

        # Variables for index calculations and entry referencing
        new_entry = HashEntry(key, value)
        hash = self._hash_function(key)
        index_init = hash % self._capacity
        probe = 1
        entry = self._buckets[index_init]
        index = index_init

        # Traverses to an available slot
        while entry is not None:
            # Restoring a previously used key
            if entry.key == key and entry.is_tombstone is True:
                self._buckets.set_at_index(index, new_entry)
                entry.is_tombstone = False
                self._size += 1
                return
            # Updating a currently used key
            elif entry.key == key:
                self._buckets.set_at_index(index, new_entry)
                return
            # Using a slot that is currently occupied by a tombstone
            elif entry.is_tombstone is True:
                self._buckets.set_at_index(index, new_entry)
                entry.is_tombstone = False
                self._size += 1
                return
            # Next index probe
            index = (index_init + probe ** 2) % self._capacity
            entry = self._buckets[index]
            probe += 1

        # Found an empty slot
        self._buckets.set_at_index(index, new_entry)
        self._size += 1


    def table_load(self) -> float:
        """
        Calculates and returns the load factor.
        """
        return self._size / self._capacity


    def empty_buckets(self) -> int:
        """
        Returns an integer of the number of empty buckets in
        the hash map.
        """
        return self._capacity - self._size


    def resize_table(self, new_capacity: int) -> None:
        """
        Updates the capacity of the current hash map to the
        specified capacity given, if valid.
        """
        # Argument validation
        if new_capacity < self._size:
            return

        # Prime capacity check
        if not self._is_prime(new_capacity):
            new_capacity = self._next_prime(new_capacity)

        # Obtains key/value pairs to be rehashed
        arr = self.get_keys_and_values()

        # Sets new capacity
        self._capacity = new_capacity

        # Rehash key/value pairs
        self.clear()
        for pair in range(arr.length()):
            (key, value) = arr[pair]
            self.put(key, value)


    def get(self, key: str) -> object:
        """
        Returns the value that is associated with the
        specified key in the hash map.
        """
        # Variables for index calculations and entry referencing
        hash = self._hash_function(key)
        index_init = hash % self._capacity
        index = index_init
        probe = 1
        entry = self._buckets[index]

        # Allows for traverses over tombstones
        spec_case = entry is not None and entry.is_tombstone is True

        # Traverses hash map to search for key
        while entry is not None or spec_case:

            # Valid key found
            if entry.key == key and entry.is_tombstone is False:
                return entry.value

            # Next index probe
            index = (index_init + probe ** 2) % self._capacity
            entry = self._buckets[index]
            spec_case = entry is not None and entry.is_tombstone is True
            probe += 1

        # Valid key not found
        return None


    def contains_key(self, key: str) -> bool:
        """
        Determines if the specified key is in the current
        hash map.
        """
        # Case of empty hash map
        if self._size == 0:
            return False

        # Variables for index calculations and entry referencing
        hash = self._hash_function(key)
        index_init = hash % self._capacity
        index = index_init
        probe = 1
        entry = self._buckets[index]

        # Allows for traverses over tombstones
        spec_case = entry is not None and entry.is_tombstone is True

        # Traverses hash map to search for key
        while entry is not None or spec_case:

            # Valid key found
            if entry.key == key and entry.is_tombstone is False:
                return True

            # Next index probe
            index = (index_init + probe ** 2) % self._capacity
            entry = self._buckets[index]
            spec_case = entry is not None and entry.is_tombstone is True
            probe += 1

        # Valid key does not exist
        return False


    def remove(self, key: str) -> None:
        """
        Removes the specified key along with its value from the
        hash map.
        """
        # Variables for index calculations and entry referencing
        hash = self._hash_function(key)
        index_init = hash % self._capacity
        index = index_init
        probe = 1
        entry = self._buckets[index]

        # Allows for traverses over tombstones
        spec_case = entry is not None and entry.is_tombstone is True

        # Traverses hash map to search for key
        while entry is not None or spec_case:

            # Valid key found and removal is performed
            if entry.key == key and entry.is_tombstone is False:
                entry.is_tombstone = True
                self._size -= 1
                return

            # Next index probe
            index = (index_init + probe ** 2) % self._capacity
            entry = self._buckets[index]
            spec_case = entry is not None and entry.is_tombstone is True
            probe += 1


    def clear(self) -> None:
        """
        Clears the contents of the current hash map without
        changing the current capacity.
        """
        # Clears contents
        self._buckets = DynamicArray()
        self._size = 0

        # Initializes empty buckets
        for index in range(self._capacity):
            self._buckets.append(None)


    def get_keys_and_values(self) -> DynamicArray:
        """
        Collects all key/values pairs in the current hash map
        and returns the collection in a DynamicArray.
        """
        # Array initialized to be returned
        new_arr = DynamicArray()

        # Traverses hash map
        for index in range(self._capacity):

            # Entry referencing
            entry = self._buckets[index]

            # Check entry validity and adds to array if valid
            if entry is not None and entry.is_tombstone is False:
                pair = (entry.key, entry.value)
                new_arr.append(pair)

        return new_arr


    def __iter__(self):
        """
        Enables iteration for HashMap class.
        """
        # Based on "Exploration: Encapsulation and Iterators"
        self._index = 0

        return self


    def __next__(self):
        """
        Returns the next active hash map entry.
        """
        try:
            # Entry referencing
            entry = self._buckets[self._index]

            # Finds next active entry
            while entry is None or entry.is_tombstone is True:
                self._index += 1
                entry = self._buckets[self._index]
        except DynamicArrayException:
            raise StopIteration

        self._index += 1
        return entry


# ------------------- BASIC TESTING ---------------------------------------- #

if __name__ == "__main__":

    print("\nPDF - put example 1")
    print("-------------------")
    m = HashMap(53, hash_function_1)
    for i in range(150):
        m.put('str' + str(i), i * 100)
        if i % 25 == 24:
            print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - put example 2")
    print("-------------------")
    m = HashMap(41, hash_function_2)
    for i in range(50):
        m.put('str' + str(i // 3), i * 100)
        if i % 10 == 9:
            print(m.empty_buckets(), round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - table_load example 1")
    print("--------------------------")
    m = HashMap(101, hash_function_1)
    print(round(m.table_load(), 2))
    m.put('key1', 10)
    print(round(m.table_load(), 2))
    m.put('key2', 20)
    print(round(m.table_load(), 2))
    m.put('key1', 30)
    print(round(m.table_load(), 2))

    print("\nPDF - table_load example 2")
    print("--------------------------")
    m = HashMap(53, hash_function_1)
    for i in range(50):
        m.put('key' + str(i), i * 100)
        if i % 10 == 0:
            print(round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - empty_buckets example 1")
    print("-----------------------------")
    m = HashMap(101, hash_function_1)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key1', 10)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key2', 20)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key1', 30)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put('key4', 40)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())

    print("\nPDF - empty_buckets example 2")
    print("-----------------------------")
    m = HashMap(53, hash_function_1)
    for i in range(150):
        m.put('key' + str(i), i * 100)
        if i % 30 == 0:
            print(m.empty_buckets(), m.get_size(), m.get_capacity())

    print("\nPDF - resize example 1")
    print("----------------------")
    m = HashMap(20, hash_function_1)
    m.put('key1', 10)
    print(m.get_size(), m.get_capacity(), m.get('key1'), m.contains_key('key1'))
    m.resize_table(30)
    print(m.get_size(), m.get_capacity(), m.get('key1'), m.contains_key('key1'))

    print("\nPDF - resize example 2")
    print("----------------------")
    m = HashMap(75, hash_function_2)
    keys = [i for i in range(25, 1000, 13)]
    for key in keys:
        m.put(str(key), key * 42)
    print(m.get_size(), m.get_capacity())

    for capacity in range(111, 1000, 117):
        m.resize_table(capacity)

        if m.table_load() > 0.5:
            print(f"Check that the load factor is acceptable after the call to resize_table().\n"
                  f"Your load factor is {round(m.table_load(), 2)} and should be less than or equal to 0.5")

        m.put('some key', 'some value')
        result = m.contains_key('some key')
        m.remove('some key')

        for key in keys:
            # all inserted keys must be present
            result &= m.contains_key(str(key))
            # NOT inserted keys must be absent
            result &= not m.contains_key(str(key + 1))
        print(capacity, result, m.get_size(), m.get_capacity(), round(m.table_load(), 2))

    print("\nPDF - get example 1")
    print("-------------------")
    m = HashMap(31, hash_function_1)
    print(m.get('key'))
    m.put('key1', 10)
    print(m.get('key1'))

    print("\nPDF - get example 2")
    print("-------------------")
    m = HashMap(151, hash_function_2)
    for i in range(200, 300, 7):
        m.put(str(i), i * 10)
    print(m.get_size(), m.get_capacity())
    for i in range(200, 300, 21):
        print(i, m.get(str(i)), m.get(str(i)) == i * 10)
        print(i + 1, m.get(str(i + 1)), m.get(str(i + 1)) == (i + 1) * 10)

    print("\nPDF - contains_key example 1")
    print("----------------------------")
    m = HashMap(11, hash_function_1)
    print(m.contains_key('key1'))
    m.put('key1', 10)
    m.put('key2', 20)
    m.put('key3', 30)
    print(m.contains_key('key1'))
    print(m.contains_key('key4'))
    print(m.contains_key('key2'))
    print(m.contains_key('key3'))
    m.remove('key3')
    print(m.contains_key('key3'))

    print("\nPDF - contains_key example 2")
    print("----------------------------")
    m = HashMap(79, hash_function_2)
    keys = [i for i in range(1, 1000, 20)]
    for key in keys:
        m.put(str(key), key * 42)
    print(m.get_size(), m.get_capacity())
    result = True
    for key in keys:
        # all inserted keys must be present
        result &= m.contains_key(str(key))
        # NOT inserted keys must be absent
        result &= not m.contains_key(str(key + 1))
    print(result)

    print("\nPDF - remove example 1")
    print("----------------------")
    m = HashMap(53, hash_function_1)
    print(m.get('key1'))
    m.put('key1', 10)
    print(m.get('key1'))
    m.remove('key1')
    print(m.get('key1'))
    m.remove('key4')

    print("\nPDF - clear example 1")
    print("---------------------")
    m = HashMap(101, hash_function_1)
    print(m.get_size(), m.get_capacity())
    m.put('key1', 10)
    m.put('key2', 20)
    m.put('key1', 30)
    print(m.get_size(), m.get_capacity())
    m.clear()
    print(m.get_size(), m.get_capacity())

    print("\nPDF - clear example 2")
    print("---------------------")
    m = HashMap(53, hash_function_1)
    print(m.get_size(), m.get_capacity())
    m.put('key1', 10)
    print(m.get_size(), m.get_capacity())
    m.put('key2', 20)
    print(m.get_size(), m.get_capacity())
    m.resize_table(100)
    print(m.get_size(), m.get_capacity())
    m.clear()
    print(m.get_size(), m.get_capacity())

    print("\nPDF - get_keys_and_values example 1")
    print("------------------------")
    m = HashMap(11, hash_function_2)
    for i in range(1, 6):
        m.put(str(i), str(i * 10))
    print(m.get_keys_and_values())

    m.resize_table(2)
    print(m.get_keys_and_values())

    m.put('20', '200')
    m.remove('1')
    m.resize_table(12)
    print(m.get_keys_and_values())

    print("\nPDF - __iter__(), __next__() example 1")
    print("---------------------")
    m = HashMap(10, hash_function_1)
    for i in range(5):
        m.put(str(i), str(i * 10))
    print(m)
    for item in m:
        print('K:', item.key, 'V:', item.value)

    print("\nPDF - __iter__(), __next__() example 2")
    print("---------------------")
    m = HashMap(10, hash_function_2)
    for i in range(5):
        m.put(str(i), str(i * 24))
    m.remove('0')
    m.remove('4')
    print(m)
    for item in m:
        print('K:', item.key, 'V:', item.value)
