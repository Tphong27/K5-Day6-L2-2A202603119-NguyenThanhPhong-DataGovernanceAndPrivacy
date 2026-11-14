def resolve_device(device):
    if device is None:
        return None
    value = str(device).strip()
    if value.lower() in ('', 'env'):
        return None
    return value


def scalar(value):
    if value is None:
        return None
    if hasattr(value, 'tolist'):
        value = value.tolist()
    if isinstance(value, (list, tuple)):
        return value[0] if value else None
    return value


def to_list(value):
    if value is None:
        return []
    if hasattr(value, 'tolist'):
        return value.tolist()
    if isinstance(value, (list, tuple)):
        return list(value)
    try:
        return list(value)
    except TypeError:
        return []


def box_points(box):
    values = to_list(box.xyxy)
    if values and isinstance(values[0], (list, tuple)):
        values = values[0]
    return [float(value) for value in values]


def class_name(names, index):
    if isinstance(names, dict):
        return names.get(index, names.get(str(index), str(index)))
    if 0 <= index < len(names):
        return names[index]
    return str(index)


def mapped_label(names, index, label_map):
    name = class_name(names, index)
    return label_map.get(name, name)


def detect(model, source, confidence=0.25, device=None, label_map=None, allowed_labels=None):
    label_map = label_map or {}
    permitted = set(allowed_labels) if allowed_labels is not None else None
    results = model.predict(source=str(source), conf=confidence, device=resolve_device(device), stream=True, verbose=False)
    for result in results:
        detections = []
        for box in result.boxes:
            label = mapped_label(result.names, int(scalar(box.cls) or 0), label_map)
            if permitted is not None and label not in permitted:
                continue
            detections.append({
                'type': 'rectangle',
                'label': label,
                'confidence': float(scalar(box.conf)),
                'points': box_points(box),
            })
        yield {'source': str(result.path), 'detections': detections}
