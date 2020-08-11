def apply(self, body):
    componentsToAdd = []
    componentsToRemove = []
    for change in body:
      if 'type' not in change:
        logging.warn('No type for change, dropping...')
        continue

      type = change['type']
      if type == 'add':
        # Add component to list
        componentsToAdd.append(change['com'])
      elif type == 'rem':
        componentsToRemove.append(change['id'])
      elif type == 'tabs':
        self.tabs = change['tabs']
        MESSAGE_DESIGNER['tabs'] = change['tabs']
      elif type == 'mov':
        target = change['com']['id']
        if target not in self.instances:
          logging.warn('Component to move not in instances [%s] -> dropping...' % (target,))
          continue
        self.instances[target].setPos(change['com']['x'], change['com']['y'])
      elif type == 'conn':
        if change['id'] not in self.instances:
          logging.warn('New connection target not in instances [%s] -> dropping...' % (change['id'],))
          continue

        self.instances[change['id']].updateConnections(change['conn'])
      else:
        logging.warn('Type not handled for change [%s] -> dropping...' % (type,))

    # Apply changes
    for id in componentsToRemove:
      if id not in self.instances:
        logging.warn('ID to remove not in instances [%s] -> dropping...' % (id,))
        continue
      del self.instances[id]

    for com in componentsToAdd:
      self.addInstance(com)

    # Save after changes
    self.save()

    # Redo MESSAGE_DESIGNER['components']
    MESSAGE_DESIGNER['components'] = []
    for instID in self.instances:
      MESSAGE_DESIGNER['components'].append(self.instances[instID].save())
    # Send to all other users
    self.sendMessage(MESSAGE_DESIGNER)