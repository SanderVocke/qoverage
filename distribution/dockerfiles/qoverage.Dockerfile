# syntax=docker/dockerfile:1
   
FROM archlinux:latest as build
WORKDIR /
RUN pacman -S --noconfirm python python-build
COPY . /qoverage
WORKDIR /qoverage
RUN python -m build -w .


FROM archlinux:latest
COPY --from=build /qoverage/dist/qoverage-*.whl /qoverage.whl
RUN pacman -S --noconfirm python python-pip qt6-declarative
RUN pip install --break-system-packages /qoverage.whl
RUN rm /qoverage.whl
ENV QMLDOM=/usr/lib/qt6/bin/qmldom
ENTRYPOINT ["qoverage"]