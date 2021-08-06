# coding=utf-8

"""Smart list of SimpleXnat items which will auto-populate when required"""


class LazyList(object):
    """Smart list of SimpleXnat items which will auto-populate when required"""
    def __init__(self, parent, wrapper_cls):
        self._list = None
        self._parent = parent
        self._wrapper_cls = wrapper_cls
        self._rest_client = parent.rest_client
        self._rest_type = wrapper_cls.rest_type
        self._optional = wrapper_cls.optional
        self._recently_created = []

    def yield_items(self):
        """Lazily populate the dictionary and yield in wrapper objects"""
        for key, item in self._get_list(allow_repopulate=True).items():
            yield self._wrapper_cls.get_existing(
                parent=self._parent,
                label=key,
                metadata=item
            )

    def get_labels(self):
        """Fetch labels for all items including newly created items"""

        return self._recently_created + \
            list(self._get_list(allow_repopulate=False).keys())

    def get_all_metadata(self):
        """Fetch metadata for all items. If items have been create since the
        previous cache of metadata, a new fetch will be triggered"""

        return self._get_list(allow_repopulate=True).values()

    def contains(self, label):
        """Return True if item exists with label"""

        return label in self._recently_created or label in \
            self._get_list(allow_repopulate=False)

    def get_metadata(self, label):
        """Return metadata for item with label, or None if it does not exist"""

        # If this is a new item, we will need the metadata to be repopulated
        repopulate = label in self._recently_created

        return self._get_list(allow_repopulate=repopulate).get(label)

    def count(self):
        """Return number of items, including cached and newly created items"""
        return len(self._recently_created) + \
            len(self._get_list(allow_repopulate=False))

    def add_new(self, label):
        """Adds a label to the list of recently created labels.
        The added label will be included in label key lists and item counts.
        If the metadata are requested for the new item then a refetch will be
        triggered when that happens"""
        self._recently_created.append(label)

    def _get_list(self, allow_repopulate=True):
        """Fetch dict of metadata.
        If allow_repopulate is True then metadata will be re-fetched if any
        new items have been created since the last cached metadata request"""

        if self._list is None or (allow_repopulate and self._recently_created):
            self._list = {
                self._wrapper_cls.find_label(item): item for item in
                self._rest_client.request_json_property(
                    uri=self._uri(), optional=self._optional)
            }
            self._recently_created = []
        return self._list

    def _uri(self):
        return '{}/{}'.format(self._parent.read_uri(), self._rest_type)
