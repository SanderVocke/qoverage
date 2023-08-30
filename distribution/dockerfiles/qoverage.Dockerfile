# syntax=docker/dockerfile:1
   
FROM archlinux:latest as build
WORKDIR /
RUN pacman -Sy --noconfirm python python-build
COPY . /qoverage
WORKDIR /qoverage
RUN python -m build -w .


FROM archlinux:latest
COPY --from=build /qoverage/dist/qoverage-*.whl /
RUN pacman -Syu --noconfirm
RUN pacman -Sy --noconfirm python python-pip qt6-declarative
RUN pip install --break-system-packages /*.whl
RUN rm /*.whl
ENV QMLDOM=/usr/lib/qt6/bin/qmldom
ENTRYPOINT ["qoverage"]