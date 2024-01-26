FROM vinixnan/pysimgrid:python-3.11

WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . /code/
RUN mkdir -p /home/pysimgrid/dots/
RUN cd /code/ && python -m pytest
RUN pysim --conf /home/pysimgrid/test/data/pl_4hosts.xml -a BatchMax -p /home/pysimgrid/test/data/basic_graph.dot

CMD ["bash"]